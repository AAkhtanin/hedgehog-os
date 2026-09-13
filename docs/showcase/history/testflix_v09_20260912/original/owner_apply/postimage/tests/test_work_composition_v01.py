"""Controlled proposals; public execution, no provider or live device lane."""
from dataclasses import fields, is_dataclass, replace
from collections.abc import Mapping
import json
import jsonschema
import sys
from pathlib import Path
import pytest
import hashlib
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import work_composition_v01 as work
from demo import run_action_packet_portability_v01 as runner
from demo import work_composition_mock_capabilities_v01 as mocks
from tests import test_execution_mode_router_g2_c_v01 as c_donor
from tests import test_continuous_delta_runtime_g2_e_v01 as e_donor
from hedgehog.kernel import fractal_runtime_v02 as g2d
from hedgehog.kernel import continuous_delta_runtime_v01 as g2e
from hedgehog.kernel import execution_mode_router_v01 as g2c
from hedgehog.kernel import transition_registry_v01 as transition


def actual_evidence_plain_v03(value):
    """Read-only test export, including immutable native ABSENT mappings."""
    if value is None or type(value) in (str, int, bool, float):
        return value
    if type(value) is abi.KernelArtifactV01:
        return abi.kernel_artifact_to_plain_dict_v01(value)
    if isinstance(value, Mapping):
        return {k: actual_evidence_plain_v03(v) for k, v in value.items()}
    if type(value) in (list, tuple):
        return [actual_evidence_plain_v03(v) for v in value]
    if is_dataclass(value):
        return {f.name: actual_evidence_plain_v03(getattr(value, f.name)) for f in fields(value)}
    raise TypeError(type(value))


def pure_setup():
    admitted = mocks.admit_playback_plan_v01('host:composition:pure')
    bridge = action.build_logical_time_bridge_v01(origin_utc_epoch_seconds=1000, seconds_per_tick=1,
        bridge_policy_version='composition.clock.v01')
    source = mocks.TrustedMockWorkSourceV01((), bridge, 1014, 'u1.controlled_utc', 'context:u1:dispatch')
    host = hosts.build_root_work_execution_host_v01(owning_root_id='root:u1:playback',
        registry=action.build_empty_action_commit_packet_registry_v02(), catalogue=(admitted,), packet_bindings=(),
        current_dependency_observations=(), logical_time_bridge=bridge, trusted_source=source)
    bsep = c_donor._c2_bsep_family(request_id='task:composition', domain_id='WORK_COMPOSITION')
    context = c_donor._c2_context_for_bsep(bsep)
    semantic = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='semantic:composition',
        artifact_type='SemanticArchitectProposal', schema_version='v1', transaction_id='transaction:composition',
        owner_root_id=host.owning_root_id, source_component='semantic_architect', authority_class='ADVISORY',
        lifecycle_state='PROPOSED', payload={'work_intent': 'derive bounded playback plan'},
        trace_refs=('intent:composition',), parent_refs=(bsep['packet']['packet_id'],),
        time_envelope={'pt_created_at': '2026-01-01T00:00:00+00:00', 'kt_asof': '2026-01-01T00:00:00+00:00',
            'et_observed_at': None, 'ct_session_anchor': 'session:composition', 'ttl_seconds': 3600,
            'freshness_class': 'static', 'valid_from': '2026-01-01T00:00:00+00:00', 'valid_to': '2026-01-01T01:00:00+00:00'})
    item = work.WorkItemV01('plan', admitted.definition.definition_id, host.owning_root_id,
        tuple(work.WorkInputBindingV01(n, work.WorkLiteralV01(action.build_action_effect_parameter_record_v01(
            parameter_name=n, value_type='REFERENCE', value=v))) for n, v in
            (('content_ref', 'content:actual:cedar'), ('device_ref', 'device:actual:one'))), (), (), None, None)
    kwargs = dict(task_id='task:composition', previous_revision_id=None, intent_ref='intent:composition',
        bsep_ref=bsep['packet']['packet_id'], semantic_proposal_ref=semantic.artifact_id,
        catalogue_revision=0, budget=work.WorkBudgetV01(8, 4, 0, 8, 0), items=(item,), trigger_evidence_refs=(),
        catalogue=(admitted,), source_context=context, semantic_proposal=semantic)
    candidate = work.build_work_program_candidate_v01(**kwargs)
    common = {k: kwargs[k] for k in ('catalogue', 'source_context', 'semantic_proposal')}
    program = work.materialize_work_program_v01(candidate, **common)
    return host, program, common, kwargs


def test_work_public_pure_execution_and_retained_input_identity():
    host, program, common, _ = pure_setup()
    results = work.advance_work_program_v01(program, **common, host_map={host.owning_root_id: host})
    assert len(results) == 1 and results[0].status == 'COMPLETED'
    assert results[0].result.output[0].value == 'would_play:content:actual:cedar@device:actual:one'
    assert (results[0].invocation, results[0].result) in host.completed_work
    assert work.validate_work_program_result_v01(program, results, **common,
        host_map={host.owning_root_id: host}) == (True, ())
    assert host.registry.action_packet_lifecycle_entries == ()


def test_work_exact_candidate_types_and_budget_and_identity():
    host, program, common, kwargs = pure_setup()
    assert work.validate_work_program_candidate_v01(program.candidate, **common) == (True, ())
    for candidate in (replace(program.candidate, catalogue_revision=1), replace(program.candidate, revision_id='revision:foreign'),
        replace(program.candidate, budget=replace(program.candidate.budget, max_compute_units=0)),
        replace(program.candidate, items=(program.candidate.items[0],) * 2)):
        assert not work.validate_work_program_candidate_v01(candidate, **common)[0]
    assert host.events == ()


def test_work_wrong_revision_or_unobserved_result_cannot_be_consumed():
    host, program, common, _ = pure_setup()
    results = work.advance_work_program_v01(program, **common, host_map={host.owning_root_id: host})
    assert not work.validate_work_program_result_v01(program, (replace(results[0], revision_id='revision:foreign'),),
        **common, host_map={host.owning_root_id: host})[0]
    other, _, _, _ = pure_setup()
    assert not work.validate_work_program_result_v01(program, results,
        **common, host_map={host.owning_root_id: other})[0]


def test_work_two_actual_compositions_share_handler_and_authorize_resolved_inputs():
    outputs = []
    for prepare in (runner.prepare_content_program_v01, runner.prepare_alarm_program_v01):
        program, common, host = prepare()
        assert host.registry.action_packet_lifecycle_entries == () and host.events == ()
        results = work.advance_work_program_v01(program, **common, host_map={host.owning_root_id: host},
            action_authorizers={host.owning_root_id: runner.authorize_resolved_work_v01})
        assert all(v.status == 'COMPLETED' for v in results), [(r.work_id, r.status, r.reasons) for r in results]
        last = results[-1]
        assert len(last.consumed_fields) >= 1
        assert last.invocation.inputs == host.completed_work[-1][0].inputs
        entry = host.registry.action_packet_lifecycle_entries[0]
        assert entry.root_bound_genesis.root_decision_projection.root_decision_result.decision == 'ACCEPT'
        assert firewall.validate_capability_business_binding_v01(common['catalogue'][-1].definition,
            last.invocation.inputs, entry.root_bound_genesis.canonical_projection) == ()
        assert [e[0] for e in host.events].index('PURE_COMPLETED') < [e[0] for e in host.events].index('ROOT_ACTION_INSTALLED')
        assert host.registry.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.adapter_call_count == 1
        outputs.append({v.parameter_name: v.value for v in last.result.output})
    assert outputs[0]['content_ref'] == 'content:composition:actual:rendered'
    assert outputs[1]['enabled'] is True and outputs[1]['alarm_state'] == 'sounding:device:composition:alarm'


def rebuild_program(program, common, **changes):
    candidate = program.candidate
    kwargs = {f: getattr(candidate, f) for f in ('task_id', 'previous_revision_id', 'intent_ref', 'bsep_ref',
        'semantic_proposal_ref', 'catalogue_revision', 'budget', 'items', 'trigger_evidence_refs')}
    kwargs.update(changes)
    return work.materialize_work_program_v01(work.build_work_program_candidate_v01(**kwargs, **common), **common)


def test_work_actual_abi_payloads_and_materialization_binding():
    host, program, common, _ = pure_setup()
    proposal = work.work_program_candidate_to_artifact_v01(program.candidate, **common)
    assert proposal.artifact_type == 'SemanticArchitectProposal' and proposal.authority_class == 'ADVISORY'
    assert abi.kernel_artifact_to_plain_dict_v01(proposal)['payload']['work_program']['items'][0]['work_id'] == 'plan'
    assert program.topology_artifact.parent_refs == (proposal.artifact_id,)
    assert len(program.source_bindings) == 3
    for binding in program.source_bindings:
        assert not abi.validate_causal_consumption_ref_v01(binding)
        assert binding.source_artifact_id == proposal.artifact_id
        assert binding.downstream_artifact_id == program.topology_artifact.artifact_id
    results = work.advance_work_program_v01(program, **common, host_map={host.owning_root_id: host})
    result = work.work_program_result_to_artifact_v01(program, results, **common, host_map={host.owning_root_id: host})
    assert not abi.validate_kernel_artifact_v01(result)
    assert (result.artifact_type, result.authority_class, result.lifecycle_state) == ('ResultProposal', 'EVIDENCE_ONLY', 'PROPOSED')
    payload = abi.kernel_artifact_to_plain_dict_v01(result)['payload']
    assert payload['work_results'][0]['invocation']['inputs'][0]['value'] == results[0].invocation.inputs[0].value
    assert not work.validate_work_program_result_v01(replace(program, source_bindings=()), results,
        **common, host_map={host.owning_root_id: host})[0]
    schema = json.loads((Path(work.__file__).resolve().parents[2] / 'schemas/work_composition_v01.schema.json').read_text())
    for kind, value in (('result_payload', payload), ('proposal_payload', abi.kernel_artifact_to_plain_dict_v01(proposal)['payload']),
        ('topology_payload', abi.kernel_artifact_to_plain_dict_v01(program.topology_artifact)['payload'])):
        schema['$ref'] = '#/$defs/' + kind
        jsonschema.Draft202012Validator(schema).validate(value)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(dict(value, authority_class='ROOT'))


def test_work_deferred_reduction_guard_false_and_completed_history_no_repeat():
    program, common, host = runner.prepare_content_program_v01()
    mapping = {host.owning_root_id: host}
    deferred = work.advance_work_program_v01(program, **common, host_map=mapping)
    assert tuple(r.status for r in deferred) == ('COMPLETED', 'COMPLETED', 'READY')
    assert host.registry.action_packet_lifecycle_entries == ()
    completed = work.advance_work_program_v01(program, **common, host_map=mapping, results=deferred,
        action_authorizers={host.owning_root_id: runner.authorize_resolved_work_v01})
    assert all(r.status == 'COMPLETED' for r in completed)
    events = host.events
    assert work.advance_work_program_v01(program, **common, host_map=mapping, results=completed) == completed
    assert host.events == events and len(host.completed_work) == 3
    with pytest.raises(ValueError, match='work_attempt_history_omitted'):
        work.advance_work_program_v01(program, **common, host_map=mapping)
    false_program, false_common, false_host = runner.prepare_alarm_program_v01(reading=4, threshold=5)
    false_results = work.advance_work_program_v01(false_program, **false_common,
        host_map={false_host.owning_root_id: false_host}, action_authorizers={false_host.owning_root_id: runner.authorize_resolved_work_v01})
    assert false_results[-1].status == 'SKIPPED_GUARD_FALSE' and false_results[-1].result is None
    assert false_host.registry.action_packet_lifecycle_entries == () and len(false_host.completed_work) == 2
    for status, reason in (('READY', 'work_root_action_required'), ('UNCERTAIN_CLOSED', 'invented_failure')):
        altered = (*false_results[:-1], replace(false_results[-1], status=status, reasons=(reason,)))
        assert not work.validate_work_program_result_v01(false_program, altered, **false_common,
            host_map={false_host.owning_root_id: false_host})[0]


def test_work_coherent_dag_contract_guard_and_budget_controls():
    program, common, host = runner.prepare_alarm_program_v01()
    observe, compare, alarm = program.candidate.items
    assert rebuild_program(program, common) == program
    invalid = (
        ((replace(observe, depends_on=('alarm',)), compare, alarm), 'work_cycle'),
        ((observe, compare, replace(alarm, depends_on=('absent',))), 'work_unknown_edge'),
        ((observe, compare, alarm, alarm), 'work_duplicate_id'),
        ((observe, compare, replace(alarm, guard=work.WorkOutputBindingV01('compare', 'missing', 'BOOLEAN'))), 'work_output_contract'),
        ((observe, compare, replace(alarm, guard=work.WorkOutputBindingV01('compare', 'exceeds', 'INTEGER'))), 'work_guard_type'),
        ((observe, compare, replace(alarm, owning_root_id='root:foreign')), 'work_foreign_root_input'),
    )
    for items, reason in invalid:
        with pytest.raises(ValueError, match=reason):
            rebuild_program(program, common, items=items)
    with pytest.raises(ValueError, match='work_budget_exhausted'):
        rebuild_program(program, common, budget=replace(program.candidate.budget, max_compute_units=2))
    unknown = rebuild_program(program, common, items=(replace(observe, definition_id='definition:unknown'), compare, alarm))
    results = work.advance_work_program_v01(unknown, **common, host_map={host.owning_root_id: host})
    assert [r.status for r in results] == ['NEEDS_CAPABILITY', 'BLOCKED_REQUIRED_OUTPUT', 'BLOCKED_REQUIRED_OUTPUT']
    assert host.events == ()
    assert not work.validate_work_program_result_v01(unknown, (replace(results[0], reasons=('arbitrary',)), *results[1:]),
        **common, host_map={host.owning_root_id: host})[0]


def test_work_field_consumption_missing_replaced_and_final_answer_controls():
    program, common, host = runner.prepare_content_program_v01()
    mapping = {host.owning_root_id: host}
    results = work.advance_work_program_v01(program, **common, host_map=mapping)
    assert results[-1].status == 'READY'
    assert results[1].invocation.inputs[0].value == results[0].result.output[0].value
    assert results[1].consumed_fields[0].source_artifact_id == results[0].result.result_id
    baseline = host.events
    admitted = common['catalogue'][0]
    invocation = results[0].invocation
    snapshot = firewall.snapshot_admitted_capability_v01(admitted)
    equivalent_output = tuple(action.build_action_effect_parameter_record_v01(
        parameter_name=v.parameter_name, value_type=v.value_type, value=v.value) for v in results[0].result.output)
    equivalent_validation = admitted.output_validator(admitted.definition, invocation, equivalent_output)
    equivalent = firewall.build_capability_execution_result_v01(invocation=invocation, admission_snapshot=snapshot,
        output=equivalent_output, output_validation=equivalent_validation)
    assert equivalent == results[0].result and equivalent is not results[0].result
    assert work.validate_work_program_result_v01(program, (replace(results[0], result=equivalent), *results[1:]),
        **common, host_map=mapping) == (True, ())
    # The designated validator sees actual changed output values. The public
    # result builder computes incidental identities itself before rejecting.
    # This is controlled rejected construction, not claimed executed output.
    for output, validator_reason, builder_reason in (
        ((), 'capability_value_missing:content_ref', 'capability_value_missing:content_ref'),
        ((action.build_action_effect_parameter_record_v01(parameter_name='content_ref', value_type='INTEGER', value=42),),
            'capability_value_type:content_ref', 'capability_value_type:content_ref'),
        ((action.build_action_effect_parameter_record_v01(parameter_name='content_ref', value_type='REFERENCE', value='content:plausible:substitute'),),
            'property_output_mismatch', 'capability_output_validation_failed'),
    ):
        negative = admitted.output_validator(admitted.definition, invocation, output)
        assert not negative.valid and negative.reason_codes == (validator_reason,)
        assert negative.subject_sha256 == firewall.capability_value_subject_sha256_v01(output)
        with pytest.raises(ValueError) as rejected:
            firewall.build_capability_execution_result_v01(invocation=invocation, admission_snapshot=snapshot,
                output=output, output_validation=negative)
        assert str(rejected.value) == builder_reason
        print('WORK_OUTPUT_CONTRACT_CONTROL=' + json.dumps(dict(validator_reason=negative.reason_codes,
            subject_sha256=negative.subject_sha256, builder_reason=str(rejected.value),
            scope='Actual designated validation and rejected public construction; no invented accepted execution.')), flush=True)
    alterations = (
        results[1:],
        (replace(results[0], revision_id='revision:foreign'), *results[1:]),
        (replace(results[0], result=results[1].result), *results[1:]),
        (replace(results[0], result=replace(results[0].result, output=())), *results[1:]),
        (replace(results[0], result=replace(results[0].result, output=(action.build_action_effect_parameter_record_v01(
            parameter_name='content_ref', value_type='INTEGER', value=42),))), *results[1:]),
        (*results[:-1], replace(results[-1], status='COMPLETED', invocation=results[1].invocation,
            result=results[1].result, reasons=())),
        (results[0], replace(results[1], consumed_fields=()), results[2]),
    )
    for altered in alterations:
        assert not work.validate_work_program_result_v01(program, altered, **common, host_map=mapping)[0]
        with pytest.raises(ValueError):
            work.advance_work_program_v01(program, **common, host_map=mapping, results=altered,
                action_authorizers={host.owning_root_id: runner.authorize_resolved_work_v01})
    assert host.events == baseline and host.registry.action_packet_lifecycle_entries == ()


def test_work_four_targets_fifth_refusal_and_independent_roots():
    devices = tuple('device:composition:four:' + str(i) for i in range(4))
    program, common, host = runner.prepare_content_program_v01(device_refs=devices)
    results = work.advance_work_program_v01(program, **common, host_map={host.owning_root_id: host},
        action_authorizers={host.owning_root_id: runner.authorize_resolved_work_v01})
    assert all(r.status == 'COMPLETED' for r in results) and len(host.registry.action_packet_lifecycle_entries) == 4
    assert {r.invocation.resource_refs for r in results if r.invocation.packet_id} == {(d,) for d in devices}
    fresh, ctx, other = runner.prepare_content_program_v01(device_refs=devices)
    first = fresh.candidate.items[2]
    bad_inputs = tuple(runner.work_literal_v01('device_ref', 'REFERENCE', 'device:composition:fifth')
        if b.input_field == 'device_ref' else b for b in first.inputs)
    wrong = rebuild_program(fresh, ctx, items=(*fresh.candidate.items[:2], replace(first, inputs=bad_inputs), *fresh.candidate.items[3:]))
    with pytest.raises(ValueError):
        work.advance_work_program_v01(wrong, **ctx, host_map={other.owning_root_id: other},
            action_authorizers={other.owning_root_id: runner.authorize_resolved_work_v01})
    assert other.registry.action_packet_lifecycle_entries == () and not any(e[0] == 'EXECUTOR_STARTED' for e in other.events)
    independent = []
    for root in ('root:composition:left', 'root:composition:right'):
        p, c, h = runner.prepare_content_program_v01(root_id=root)
        r = work.advance_work_program_v01(p, **c, host_map={root: h}, action_authorizers={root: runner.authorize_resolved_work_v01})
        assert all(v.status == 'COMPLETED' for v in r)
        independent.append((p, c, h, r))
    left, right = independent
    assert left[2].registry != right[2].registry
    assert not work.validate_work_program_result_v01(left[0], left[3], **left[1],
        host_map={left[2].owning_root_id: right[2]})[0]
    assert left[2].registry.action_packet_lifecycle_entries[0].root_bound_genesis.canonical_projection.owning_local_root_id == 'root:composition:left'
    assert right[2].registry.action_packet_lifecycle_entries[0].root_bound_genesis.canonical_projection.owning_local_root_id == 'root:composition:right'


def test_work_started_uncertain_is_observed_and_never_reduced_to_retry():
    root, device = 'root:composition:uncertain', 'device:composition:uncertain'
    admitted = mocks.admit_playback_variant_v01(device, 'host:' + root, mocks.execute_playback_uncertain_v01)
    item = work.WorkItemV01('display', admitted.definition.definition_id, root,
        (runner.work_literal_v01('content_ref', 'REFERENCE', 'content:composition:uncertain'),
         runner.work_literal_v01('device_ref', 'REFERENCE', device)), (device,), (), None, None)
    program, common, host = runner.prepare_work_program_v01(task_id='task:composition:uncertain', root_id=root,
        admitted=(admitted,), items=(item,), device_refs=(device,))
    results = work.advance_work_program_v01(program, **common, host_map={root: host},
        action_authorizers={root: runner.authorize_resolved_work_v01})
    assert results[0].status == 'UNCERTAIN_CLOSED'
    assert host.work_attempts[0].disposition == results[0].status
    assert any(e[0] == 'EXECUTOR_STARTED' for e in host.events)
    assert host.registry.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.adapter_call_count == 1
    events = host.events
    assert work.advance_work_program_v01(program, **common, host_map={root: host}, results=results) == results
    assert host.events == events
    with pytest.raises(ValueError, match='work_attempt_history_omitted'):
        work.advance_work_program_v01(program, **common, host_map={root: host})
    assert not work.validate_work_program_result_v01(program,
        (replace(results[0], status='FAILED_NON_CONSUMING'),), **common, host_map={root: host})[0]


@pytest.fixture(scope='session')
def actual_deep_source(request):
    """One actual public D run shared by related controls, not a stored report."""
    return e_donor._retained_shared_baseline_v06(request)


def prepare_exact_review_work(reading=19, *, task_id='task:composition:exact_review',
    root_id='root:composition:exact_review', work_id='reviewed_observe', semantic_suffix=''):
    admitted = mocks.admit_pure_operation_v01(operation_id='u1.reviewed_observation',
        input_fields=(('reading', 'INTEGER'),), output_fields=(('observed_level', 'INTEGER'),),
        executor=mocks.observe_level_v01, output_validator=mocks.validate_level_output_v01,
        host_instance_ref='host:' + root_id)
    item = work.WorkItemV01(work_id, admitted.definition.definition_id, root_id,
        (runner.work_literal_v01('reading', 'INTEGER', reading),), (), (), None, None)
    program, common, host = runner.prepare_work_program_v01(task_id=task_id, root_id=root_id,
        admitted=(admitted,), items=(item,), device_refs=())
    if semantic_suffix:
        old = common['semantic_proposal']
        plain = abi.kernel_artifact_to_plain_dict_v01(old)
        semantic = abi.build_kernel_artifact_v01(**dict(plain, artifact_id=old.artifact_id + semantic_suffix,
            trace_refs=tuple(plain['trace_refs']), parent_refs=tuple(plain['parent_refs'])))
        common = dict(common, semantic_proposal=semantic)
        program = rebuild_program(program, common, semantic_proposal_ref=semantic.artifact_id)
    return program, common, host


def build_exact_review_source(program, common, *, blocked=False):
    candidate = program.candidate
    item = candidate.items[0]
    scope = work.build_work_review_scope_ref_v01(candidate=candidate, item=item,
        source_context=common['source_context'], semantic_proposal=common['semantic_proposal'])
    identities = dict(request_id=candidate.task_id, transaction_id=common['semantic_proposal'].transaction_id,
        owning_root_id=item.owning_root_id, domain_id=common['source_context'].business_request_context_packet['domain'])
    profiles = tuple(g2c.build_execution_mode_local_mode_profile_v01(**identities, mode=mode,
        policy_snapshot_id='policy:composition:exact_review', capability_snapshot_id='caps:composition:exact_review',
        cost_model_id='cost:composition:exact_review', policy_allowed=mode == 'full_fractal', scope_allowed=True,
        risk_allowed=True, privacy_allowed=True,
        capability_state='NOT_REQUIRED' if mode in ('sealed_replay', 'direct_informational_reuse') else 'AVAILABLE',
        capability_id=None if mode in ('sealed_replay', 'direct_informational_reuse') else 'capability:review:' + mode,
        cost_units=index + 1) for index, mode in enumerate(g2c.EXECUTABLE_EXECUTION_MODES_V01))
    snapshot = g2c.build_execution_mode_local_routing_snapshot_v01(**identities,
        request_class='BOUNDED_REVIEW', action_class='NON_ACTION', action_packet_relation='NOT_APPLICABLE',
        scope_class='BOUNDED', scope_ref=scope, permitted_narrower_scope_refs=(), risk_class='LOW',
        policy_snapshot_id='policy:composition:exact_review', capability_snapshot_id='caps:composition:exact_review',
        cost_model_id='cost:composition:exact_review', required_user_input_state='COMPLETE', hard_block_state='CLEAR',
        evaluation_time_epoch_seconds=1767225600, pt_created_at_utc='2026-01-01T00:00:00+00:00',
        et_observed_at_utc='2026-01-01T00:00:00+00:00', ct_session_anchor='session:exact_review', ttl_seconds=3600,
        freshness_class='static', valid_from_utc='2026-01-01T00:00:00+00:00', valid_to_utc='2026-01-01T01:00:00+00:00',
        mode_profiles=profiles)
    old = common['source_context']
    source = g2c.build_execution_mode_source_context_v01(**dict({f.name: getattr(old, f.name) for f in fields(old)},
        g2a_evaluation_time=snapshot.evaluation_time_epoch_seconds, g2a_evaluation_time_source=snapshot.created_by,
        g2a_evaluation_context_id=snapshot.local_routing_snapshot_id))
    routing = g2c.build_execution_mode_router_input_v01(request_id=candidate.task_id,
        transaction_id=identities['transaction_id'], owning_root_id=item.owning_root_id,
        bsep_binding=g2c.build_execution_mode_bsep_binding_v01(**identities, source_context=source),
        local_routing_snapshot=snapshot,
        replay_binding=g2c.build_execution_mode_replay_not_applicable_binding_v01(**identities),
        g2a_binding=g2c.build_execution_mode_g2a_no_packet_binding_v01(**identities,
            evaluation_time=snapshot.evaluation_time_epoch_seconds, evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id),
        g2b_binding=g2c.build_execution_mode_g2b_not_applicable_binding_v01(**identities))
    proposal, report = g2c.route_execution_mode_v01(router_input=routing, source_context=source)
    assert report.validation_status == 'PASS' and proposal.selected_mode == 'full_fractal'
    proposal_artifact = g2c.project_execution_mode_proposal_kernel_artifact_v01(
        proposal=proposal, router_input=routing, source_context=source)
    registry = transition.build_execution_mode_transition_registry_profile_v01()
    before = g2c.evaluate_execution_mode_proposal_to_root_transition_v01(registry=registry,
        proposal=proposal, router_input=routing, source_context=source, proposal_artifact=proposal_artifact)
    review = g2c.build_root_execution_mode_review_input_v01(proposal=proposal, router_input=routing,
        source_context=source, proposal_artifact=proposal_artifact, proposal_transition_decision=before,
        review_action='REJECT' if blocked else 'ACCEPT', accepted_scope_ref=None if blocked else scope, narrowing_basis_refs=())
    decision, kernel, root_input, root_result, reviewed = g2c.review_execution_mode_proposal_v01(review_input=review,
        proposal=proposal, router_input=routing, source_context=source, proposal_artifact=proposal_artifact,
        proposal_transition_decision=before)
    assert reviewed.validation_status == 'PASS'
    assert decision.accepted_scope_ref == (None if blocked else scope)
    assert decision.outcome == ('REJECT' if blocked else 'ACCEPT')
    roots = dict(review_input=review, decision=decision, proposal=proposal, router_input=routing,
        source_context=source, proposal_artifact=proposal_artifact, proposal_transition_decision=before,
        root_kernel=kernel, root_decision_input=root_input, root_decision_result=root_result)
    decision_artifact = g2c.project_root_execution_mode_decision_kernel_artifact_v01(**roots)
    after = g2c.evaluate_execution_mode_root_route_transition_v01(registry=registry,
        **roots, decision_artifact=decision_artifact)
    route = g2c.project_execution_mode_route_eligibility_kernel_artifact_v01(**roots,
        decision_artifact=decision_artifact, root_route_transition_decision=after)
    policy = g2d.build_fractal_runtime_policy_v02(required_downstream_capability_ids=proposal.required_downstream_capability_ids,
        permitted_child_scope_refs=())
    source_arguments = dict(transition_registry=registry,
        g2c_source_context=source, router_input=routing, proposal=proposal, proposal_artifact=proposal_artifact,
        proposal_transition_decision=before, review_input=review, decision=decision, root_kernel=kernel,
        root_decision_input=root_input, root_decision_result=root_result, decision_artifact=decision_artifact,
        root_route_transition_decision=after, route_eligibility_artifact=route, runtime_policy=policy)
    if blocked:
        assert route is None
        return source_arguments, dict(common, source_context=source)
    runtime_source = g2d.build_fractal_runtime_source_context_v02(**source_arguments)
    return runtime_source, dict(common, source_context=source)


def attach_review(program, common, source):
    item = replace(program.candidate.items[0], review_obligation_id=None)
    base = rebuild_program(program, common, items=(item,))
    obligation = work.build_work_review_obligation_v01(candidate=base.candidate, item=item, source_context=source)
    item = replace(item, review_obligation_id=obligation.obligation_id)
    final = rebuild_program(base, common, items=(item,))
    obligation = work.build_work_review_obligation_v01(candidate=final.candidate, item=item, source_context=source)
    return final, obligation


@pytest.fixture(scope='module')
def exact_review_cases():
    cases = []
    for reading in (19, 23):
        program, common, host = prepare_exact_review_work(reading)
        source, common = build_exact_review_source(program, common)
        bundle, report = g2d.run_fractal_runtime_v02(source)
        assert report.status == 'PASS' and bundle is not None
        assert g2d.validate_fractal_runtime_execution_bundle_v02(bundle).status == 'PASS'
        program, obligation = attach_review(program, common, source)
        assert work.build_work_review_scope_ref_v01(candidate=program.candidate, item=program.candidate.items[0],
            source_context=common['source_context'], semantic_proposal=common['semantic_proposal']) == source.decision.accepted_scope_ref
        cases.append(dict(reading=reading, program=program, common=common, host=host, source=source,
            bundle=bundle, obligation=obligation))
    return cases


def check_exact_review(case, *, program=None, obligation=None, source=None, bundle=None, semantic=None):
    program = case['program'] if program is None else program
    return work.validate_work_review_binding_v01(case['obligation'] if obligation is None else obligation,
        candidate=program.candidate, item=program.candidate.items[0],
        source_context=case['source'] if source is None else source,
        execution_bundle=case['bundle'] if bundle is None else bundle,
        semantic_proposal=case['common']['semantic_proposal'] if semantic is None else semantic)


def test_work_required_public_d_review_readiness_and_reused_completion(exact_review_cases):
    case = exact_review_cases[0]
    program, common, host, source, bundle, obligation = (case[k] for k in ('program','common','host','source','bundle','obligation'))
    item = program.candidate.items[0]
    bindings = ((obligation, source, bundle),)
    assert check_exact_review(case) == (True, ())
    mapping = {item.owning_root_id: host}
    blocked = work.advance_work_program_v01(program, **common, host_map=mapping)
    assert blocked[0].status == 'BLOCKED_INVALID_INPUT' and blocked[0].reasons == ('work_required_review_missing',)
    assert host.events == ()
    completed = work.advance_work_program_v01(program, **common, host_map=mapping, results=blocked, review_bindings=bindings)
    assert completed[0].status == 'COMPLETED' and completed[0].result.output[0].value == 19
    assert not work.validate_work_program_result_v01(program, completed, **common, host_map=mapping)[0]
    with pytest.raises(ValueError, match='work_required_review_missing'):
        work.advance_work_program_v01(program, **common, host_map=mapping, results=completed)
    for bad in (replace(obligation, work_id='other'), replace(obligation, owning_root_id='root:foreign'),
        replace(obligation, revision_id='revision:wrong')):
        assert not check_exact_review(case, obligation=bad)[0]
    # A structurally rebuilt negative runtime report is not completed D work.
    bad_report = replace(bundle.runtime_report, runtime_outcome='BLOCKED')
    bad_report = replace(bad_report, report_id=g2d.rebuild_fractal_runtime_report_identity_v02(bad_report))
    assert not check_exact_review(case, bundle=replace(bundle, runtime_report=bad_report))[0]
    events = host.events
    assert work.advance_work_program_v01(program, **common, host_map=mapping, results=completed, review_bindings=bindings) == completed
    assert host.events == events
    equivalent_item = replace(item, inputs=tuple(replace(b, source=replace(b.source, value=action.build_action_effect_parameter_record_v01(
        parameter_name=b.source.value.parameter_name, value_type=b.source.value.value_type, value=b.source.value.value))) for b in item.inputs))
    equivalent = rebuild_program(program, common, items=(equivalent_item,))
    assert equivalent == program and equivalent is not program and equivalent_item is not item
    equivalent_obligation = work.build_work_review_obligation_v01(candidate=equivalent.candidate,
        item=equivalent_item, source_context=source)
    assert check_exact_review(case, program=equivalent, obligation=equivalent_obligation) == (True, ())
    case['completed_results'] = completed
    print('EXACT_WORK_REVIEW=' + json.dumps(dict(reading=19, scope=source.decision.accepted_scope_ref,
        runtime_outcome=bundle.runtime_report.runtime_outcome, result_value=completed[0].result.output[0].value,
        missing_review=blocked[0].reasons, equivalent=True), sort_keys=True), flush=True)


def test_work_e_public_budget_reuse_constraints(actual_deep_source, retained_native_execution_v05):
    _, _, baseline = actual_deep_source
    root = next(i for i in baseline.cell_inputs if i.parent_cell_id is None)
    selected_id, sibling_id = root.ordered_planned_child_cell_ids
    selected = next(r for r in baseline.cell_results if r.cell_id == selected_id)
    cell_input = next(i for i in baseline.cell_inputs if i.cell_id == selected_id)
    budgets = {b.budget_id: b for b in baseline.budgets}
    entries = {q.queue_entry_id: q for q in baseline.queue_entries}
    index = baseline.cell_results.index(selected)
    report = next(r for r in baseline.validation_reports if r.validation_report_id == selected.pre_result_validation_report_id)
    kwargs = dict(topology=baseline.topology, cell_input=cell_input,
        terminal_queue_entries=tuple(entries[q] for q in selected.ordered_terminal_queue_entry_ids), child_results=(),
        accepted_output_refs=selected.accepted_output_refs, evidence_refs=selected.evidence_refs,
        pre_result_validation_report=report, post_vv_report=baseline.post_vv_reports[index],
        gt_advisory_report=baseline.gt_advisory_reports[index], partial_failures=(),
        allocated_cell_budget=budgets[selected.allocated_cell_budget_id],
        final_cell_budget=budgets[selected.final_cell_budget_id], global_budget=budgets[selected.global_budget_id])
    equivalent = g2d.build_fractal_cell_result_v02(**kwargs)
    assert equivalent == selected and equivalent is not selected
    # Counterfactual structural construction, NOT a claimed accepted E result:
    # any changed retained result field changes the public aggregation anchor.
    altered = g2d.build_fractal_cell_result_v02(**dict(kwargs,
        accepted_output_refs=(*selected.accepted_output_refs, 'ref:controlled:changed_output')))
    assert altered.result_id != selected.result_id
    aggregate = next(b for b in baseline.budgets if b.budget_event_kind == 'CHILD_AGGREGATE' and b.budget_event_ref == selected.result_id)
    args = dict(policy=baseline.source_context.runtime_policy, topology_seed=baseline.topology_seed,
        allocation_parent_budget=None, predecessor_budget=budgets[aggregate.predecessor_budget_id],
        owning_cell_id=root.cell_id, budget_scope='ROOT_GLOBAL_AND_CELL', budget_state='ACTIVE',
        budget_event_kind='CHILD_AGGREGATE', budget_context_input=root, canonical_child_index=0,
        allocation_queue_entries=(), transition_decision=None, paired_cell_budget=budgets[selected.final_cell_budget_id])
    assert g2d.build_fractal_runtime_budget_v02(**args, child_result=equivalent) == aggregate
    changed_aggregate = g2d.build_fractal_runtime_budget_v02(**args, child_result=altered)
    assert changed_aggregate.budget_event_ref == altered.result_id and changed_aggregate.budget_id != aggregate.budget_id
    sibling = next(i for i in baseline.cell_inputs if i.cell_id == sibling_id)
    chain = []
    cursor = budgets[sibling.global_budget_id]
    while cursor is not None:
        chain.append(cursor.budget_id)
        cursor = budgets.get(cursor.predecessor_budget_id)
    assert aggregate.budget_id in chain and changed_aggregate.budget_id not in chain
    poisoned = replace(baseline, budgets=tuple(changed_aggregate if b == aggregate else b for b in baseline.budgets))
    assert g2d.validate_fractal_runtime_execution_bundle_v02(poisoned).status == 'FAIL_CLOSED'
    retained = retained_native_execution_v05['result'].recomputed_g2d_execution_bundle
    assert retained_native_execution_v05['supplied_d'].status == 'PASS'
    assert g2d.fractal_runtime_execution_bundle_to_plain_data_v02(retained.observed_work_context.baseline_execution_bundle) == g2d.fractal_runtime_execution_bundle_to_plain_data_v02(baseline)
    retained_parent = next(r for r in retained.cell_results if r.parent_cell_id is None)
    history = retained.retained_consumptions[0].consumed_result
    assert history.result_id in retained_parent.ordered_child_result_ids
    assert history not in retained.cell_results
    assert not any(b.owning_cell_id == history.cell_id for b in retained.budgets)

    print('E_BUDGET_REUSE_CONSTRAINT=' + json.dumps(dict(
        selected_result=selected.result_id, changed_structural_result=altered.result_id,
        original_aggregate=aggregate.budget_id, changed_aggregate=changed_aggregate.budget_id,
        retained_sibling_input=sibling.cell_input_id, retained_sibling_global_budget=sibling.global_budget_id,
        retained_predecessor_chain=chain,
        scope='Public equivalent control plus counterfactual identity/ancestry test; not an accepted recomputation.'), sort_keys=True), flush=True)


def native_e_packet(transaction_id):
    device = 'device:composition:e_alarm'
    admitted = mocks.admit_alarm_v01(device, 'host:composition:e_alarm')
    inputs = tuple(action.build_action_effect_parameter_record_v01(parameter_name=n, value_type=t, value=v)
        for n, t, v in (('device_ref', 'REFERENCE', device), ('enabled', 'BOOLEAN', True)))
    scaffold = runner.build_native_work_action_v01(admitted=admitted, inputs=inputs,
        root_id=e_donor._E3_ROOT, transaction_id=transaction_id, business_object_ref='signal:composition:e_alarm')
    dependency = e_donor._e3_g2a_dependency()
    canonical = action.build_native_action_commit_packet_v01(transaction_id=transaction_id,
        owning_local_root_id=e_donor._E3_ROOT, canonical_permission_ref=scaffold.canonical_permission_ref,
        selected_canonical_action=scaffold.selected_canonical_action, normalized_subject_scope=scaffold.normalized_subject_scope,
        normalized_target_scope=scaffold.normalized_target_scope, normalized_permission_scope=scaffold.normalized_permission_scope,
        adapter_binding=scaffold.adapter_binding, dependency_candidate=dependency,
        temporal_authority=action.build_action_temporal_authority_profile_v01(issued_at_utc=e_donor._E3_VALID_FROM,
            expires_at_utc=e_donor._E3_VALID_TO, ttl_seconds=e_donor._E3_VALID_TO-e_donor._E3_VALID_FROM,
            temporal_policy_version='u1.logical_utc.v01'), authority_policy=scaffold.authority_policy,
        business_object_identity=scaffold.business_object_identity,
        consequential_effect_parameters=scaffold.consequential_effect_parameters,
        evaluation_time=e_donor._E3_TIME-4, evaluation_time_source='g2e_e3_trusted_ceiling',
        evaluation_context_id='evaluation_context:g2e:e3:g2a', admitted_capability=admitted, inputs=inputs)
    prepared = runner.authorize_and_prepare_action_v01(canonical, admitted, inputs)
    packet = prepared.root_bound
    dep = dependency.dependency_records[0]
    invalidation = action.build_action_invalidation_evidence_v01(source_invalidation_event_ref='event:composition:e:changed',
        packet_id=packet.packet_identity.packet_id, dependency_id=dep.dependency_id, invalidation_class='DEPENDENCY_CHANGED',
        evidence_ref=dep.evidence_ref, evidence_sha256=e_donor._sha('composition-actual-changed-dependency'), observed_status='CHANGED',
        time_envelope_id=dep.time_envelope_id, freshness_policy_id=dep.freshness_policy_id,
        owning_local_root_id=e_donor._E3_ROOT, accepted_by_local_root_id=e_donor._E3_ROOT, authority_effect='DETERMINISTIC_BLOCK',
        evaluation_time=e_donor._E3_TIME, evaluation_time_source='g2e_e3_trusted_ceiling', evaluation_context_id='evaluation_context:g2e:e3:g2a')
    assert action.validate_action_invalidation_evidence_against_packet_v01(invalidation, packet) == (True, ())
    return prepared, dict(packet=packet, registry=prepared.registry, dependency=dependency,
        observations=prepared.observations, invalidation=invalidation)


def test_capture_material_local_scope_origin_mutation_and_lifetime_v06():
    import sys
    from types import MappingProxyType

    prepared, _ = native_e_packet('transaction:composition:capture-scope:v06')
    trusted = e_donor.TemporalCountingSourceV03(mocks.TrustedMockWorkSourceV01(
        prepared.observations, prepared.bridge, e_donor._E3_TIME + 35,
        'g2e_e3_trusted_ceiling', 'evaluation_context:g2e:e3:g2a'))
    host = runner.host_for_prepared_action_v01(prepared, trusted)
    capture = hosts.capture_current_action_source_v01(host,
        packet_id=prepared.root_bound.packet_identity.packet_id, expected_revision=host.revision,
        evaluation_time=e_donor._E3_TIME + 35, evaluation_time_source='g2e_e3_trusted_ceiling',
        evaluation_context_id='evaluation_context:g2e:e3:g2a')
    foreign_prepared, _ = native_e_packet('transaction:composition:capture-scope:foreign:v06')
    foreign = runner.host_for_prepared_action_v01(foreign_prepared, trusted)
    reads, calls = trusted.reads, mocks.observed_mock_calls_v01()
    counts, outcomes = [], {}
    code = hosts._capture_sources_valid_v01.__code__
    tool = next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
    sys.monitoring.use_tool_id(tool, 'capture_material_full_calls_v06')
    sys.monitoring.register_callback(tool, sys.monitoring.events.PY_START,
        lambda c, offset: counts.append(c.co_name))
    sys.monitoring.set_local_events(tool, code, sys.monitoring.events.PY_START)
    def check(name, value=capture, *, owner=host, current=True, refusal=False):
        if refusal:
            with pytest.raises(ValueError) as rejected:
                hosts.validate_retained_action_source_capture_v01(owner, value, require_current=current)
            outcomes[name] = str(rejected.value)
        else:
            assert hosts.validate_retained_action_source_capture_v01(owner, value, require_current=current)
            outcomes[name] = 'PASS'
    try:
        with hosts._capture_validation_scope_v06():
            scope = hosts._CAPTURE_VALIDATION_SCOPE_V06.get()
            check('actual'); check('actual_repeat')
            assert len(counts) == 1 and len(scope.entries) == 1
            assert scope.entries[0][2].supported
            check('equivalent', replace(capture))
            assert len(counts) == 2
            check('wrong_origin', replace(capture, _origin=object()), refusal=True)
            check('foreign_host', owner=foreign, refusal=True)
            check('wrong_ordinal', replace(capture, capture_ordinal=1), refusal=True)
            for name, changed in (('packet_id', 'packet:foreign'), ('owning_root_id', 'root:foreign'),
                ('source_revision', capture.source_revision + 1),
                ('evaluation_time', capture.evaluation_time + 1)):
                check('wrong_' + name, replace(capture, **{name: changed}), refusal=True)
            check('positive_after_refusals')
            before = len(counts)
            # Busy is the internal reentry boundary: it must do the real check.
            scope.busy = True
            try:
                check('busy_fallback')
            finally:
                scope.busy = False
            assert len(counts) == before + 1

            identity = capture.root_bound_packet.packet_identity
            material = list(identity.material)
            index = next(i for i, item in enumerate(material) if type(item[1]) is MappingProxyType)
            backing = dict(material[index][1])
            material[index] = (material[index][0], MappingProxyType(backing))
            mutable_copy = replace(capture, root_bound_packet=replace(capture.root_bound_packet,
                packet_identity=replace(identity, material=tuple(material))))
            assert mutable_copy == capture
            check('independent_mutable_positive', mutable_copy)
            check('independent_mutable_repeat', mutable_copy)
            before = len(counts)
            original_items = dict(backing)
            backing['scope_mutation_v06'] = True
            check('changed_nested_material', mutable_copy, refusal=True)
            assert len(counts) == before + 1
            backing.clear(); backing.update(original_items)
            check('restored_equivalent', mutable_copy)

            unsupported = replace(capture)
            object.__setattr__(unsupported, '_unrecognized_material', object())
            before = len(counts)
            check('unknown_form_fallback_1', unsupported)
            check('unknown_form_fallback_2', unsupported)
            assert len(counts) == before + 2
            assert not hosts._CaptureMaterialEdgesV06(unsupported).supported
            with pytest.raises(RuntimeError, match='scope-exception'):
                with hosts._capture_validation_scope_v06():
                    check('nested_scope_positive')
                    raise RuntimeError('scope-exception')
            assert not scope.entries
            before = len(counts)
            check('after_exception')
            assert len(counts) == before + 1
        assert hosts._CAPTURE_VALIDATION_SCOPE_V06.get() is None
        before = len(counts)
        check('independent_call_1'); check('independent_call_2')
        assert len(counts) == before + 2
        assert trusted.reads == reads and mocks.observed_mock_calls_v01() == calls
        with hosts._capture_validation_scope_v06():
            check('before_advance')
            trusted.advance_v01(evaluation_time=e_donor._E3_TIME + 36, observations=capture.observations)
            fresh = hosts.capture_current_action_source_v01(host, packet_id=capture.packet_id,
                expected_revision=host.revision, evaluation_time=e_donor._E3_TIME + 36,
                evaluation_time_source=capture.evaluation_time_source,
                evaluation_context_id=capture.evaluation_context_id)
            assert trusted.reads > reads
            reads = trusted.reads
            check('old_historical', current=False)
            check('old_current_refusal', refusal=True)
            check('fresh_current', fresh)
            assert trusted.reads == reads and mocks.observed_mock_calls_v01() == calls
    finally:
        sys.monitoring.set_local_events(tool, code, 0)
        sys.monitoring.free_tool_id(tool)
    assert hosts._CAPTURE_VALIDATION_SCOPE_V06.get() is None
    print('CAPTURE_SCOPE_V06=' + json.dumps(dict(outcomes=outcomes,
        full_material_calls=len(counts), no_validation_live_reads=True, mock_effect_delta=0,
        supported_real_capture=True, independent_calls_validate=True)), flush=True)


def test_capture_receipt_material_reuse_and_mutation_v08():
    prepared, _ = native_e_packet('transaction:composition:receipt-scope:v08')
    trusted = e_donor.TemporalCountingSourceV03(mocks.TrustedMockWorkSourceV01(
        prepared.observations, prepared.bridge, e_donor._E3_TIME,
        'u1.controlled_utc', 'context:u1:dispatch'))
    host = runner.host_for_prepared_action_v01(prepared, trusted)
    packet = prepared.root_bound.packet_identity.packet_id
    clock = dict(evaluation_time=e_donor._E3_TIME,
        evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:dispatch')
    hosts.dispatch_current_action_v01(host, packet_id=packet, task_id='task:receipt-scope:v08',
        expected_revision=host.revision, **clock)
    trusted.advance_v01(evaluation_time=e_donor._E3_TIME + 35, observations=prepared.observations)
    clock = dict(clock, evaluation_time=e_donor._E3_TIME + 35)
    capture = hosts.capture_current_action_source_v01(host, packet_id=packet,
        expected_revision=host.revision, **clock)
    contexts = capture.registry.action_packet_fulfillment_attempt_contexts
    assert len(contexts) == 1 and contexts[0].receipt is not None
    receipt = contexts[0].receipt
    assert type(receipt) is abi.KernelArtifactV01
    assert type(receipt.payload) is type(receipt.time_envelope) is abi._FrozenJSONObject
    receipt_copy = replace(receipt, payload=replace(receipt.payload), time_envelope=replace(receipt.time_envelope))
    context_copy = replace(contexts[0], receipt=receipt_copy,
        request=replace(contexts[0].request), decision=replace(contexts[0].decision))
    equivalent = replace(capture, registry=replace(capture.registry,
        action_packet_fulfillment_attempt_contexts=(context_copy,)))
    assert equivalent == capture and equivalent is not capture
    reads, calls = trusted.reads, mocks.observed_mock_calls_v01()
    counts, outcomes = [], {}
    code = hosts._capture_sources_valid_v01.__code__
    tool = next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
    sys.monitoring.use_tool_id(tool, 'capture_receipt_material_v08')
    sys.monitoring.register_callback(tool, sys.monitoring.events.PY_START,
        lambda c, offset: counts.append(c.co_name))
    sys.monitoring.set_local_events(tool, code, sys.monitoring.events.PY_START)
    def check(name, value=equivalent, *, refusal=False, current=True):
        if refusal:
            with pytest.raises(ValueError) as error:
                hosts.validate_retained_action_source_capture_v01(host, value, require_current=current)
            outcomes[name] = str(error.value)
        else:
            assert hosts.validate_retained_action_source_capture_v01(host, value, require_current=current)
            outcomes[name] = 'PASS'
    try:
        with hosts._capture_validation_scope_v06():
            scope = hosts._CAPTURE_VALIDATION_SCOPE_V06.get()
            check('historical_receipt'); check('same_receipt_repeat')
            assert len(counts) == 1 and len(scope.entries) == 1
            material = scope.entries[0][2]
            assert material.supported and material.unchanged()
            assert any(type(row[0]) is abi.KernelArtifactV01 for row in material.rows)
            assert any(type(row[0]) is abi._FrozenJSONObject for row in material.rows)
            for name, target, attribute, changed in (
                ('payload_items', receipt_copy.payload, 'items', receipt_copy.payload.items + (('unknown_receipt_field', True),)),
                ('time_items', receipt_copy.time_envelope, 'items', receipt_copy.time_envelope.items + (('unknown_time_field', True),)),
                ('receipt_identity', receipt_copy, 'artifact_id', receipt_copy.artifact_id + ':substituted'),
                ('request_slot', context_copy.request, 'request_id', context_copy.request.request_id + ':substituted'),
                ('decision_slot', context_copy.decision, 'request_id', context_copy.decision.request_id + ':substituted'),
                ('receipt_reference', context_copy, 'receipt', replace(receipt_copy, trace_refs=('trace:foreign',)))):
                old = getattr(target, attribute); before = len(counts)
                try:
                    object.__setattr__(target, attribute, changed)
                    check(name, refusal=True)
                    assert len(counts) == before + 1
                finally:
                    object.__setattr__(target, attribute, old)
                check('restored_' + name)
            check('wrong_actual_origin', replace(equivalent, _origin=object()), refusal=True)
            check('wrong_ordinal', replace(equivalent, capture_ordinal=99), refusal=True)
            check('original_positive', capture)
            class UnknownReceipt(abi.KernelArtifactV01):
                pass
            unknown = UnknownReceipt(**receipt.__dict__)
            assert not hosts._CaptureMaterialEdgesV06(replace(capture, registry=replace(capture.registry,
                action_packet_fulfillment_attempt_contexts=(replace(contexts[0], receipt=unknown),)))).supported
            with pytest.raises(RuntimeError, match='receipt_scope_exception'):
                with hosts._capture_validation_scope_v06():
                    check('before_exception')
                    raise RuntimeError('receipt_scope_exception')
            assert not scope.entries
            before = len(counts); check('after_exception')
            assert len(counts) == before + 1
        assert hosts._CAPTURE_VALIDATION_SCOPE_V06.get() is None
        before = len(counts); check('independent_public_call')
        assert len(counts) == before + 1
        assert trusted.reads == reads and mocks.observed_mock_calls_v01() == calls
        assert abi.kernel_artifact_to_plain_dict_v01(receipt_copy) == abi.kernel_artifact_to_plain_dict_v01(receipt)
        trusted.advance_v01(evaluation_time=e_donor._E3_TIME + 36, observations=capture.observations)
        fresh = hosts.capture_current_action_source_v01(host, packet_id=packet,
            expected_revision=host.revision, **dict(clock, evaluation_time=e_donor._E3_TIME + 36))
        reads = trusted.reads
        check('old_historical_after_advance', capture, current=False)
        check('old_current_after_advance', capture, refusal=True)
        check('fresh_current', fresh)
        assert trusted.reads == reads and mocks.observed_mock_calls_v01() == calls
    finally:
        sys.monitoring.set_local_events(tool, code, 0)
        sys.monitoring.free_tool_id(tool)
    print('CAPTURE_RECEIPT_V08=' + json.dumps(dict(outcomes=outcomes, full_material_calls=len(counts),
        receipt_id=receipt.artifact_id, lifecycle_entries=len(capture.registry.action_packet_lifecycle_entries),
        fulfillment_contexts=len(contexts), validation_reads=0, validation_effects=0)), flush=True)


def test_native_e_source_and_real_selective_recomputation(actual_deep_source, retained_native_execution_v05, exact_review_cases):
    g2b, family, baseline = actual_deep_source
    prepared, native = native_e_packet(str(g2b['transaction_id']))
    legacy = e_donor._e3_g2a_family(str(g2b['transaction_id']))
    root_input = next(c for c in baseline.cell_inputs if c.parent_cell_id is None)
    baseline_bytes = e_donor.canonical_json_bytes_v01(e_donor._e3_public_plain(baseline))
    outcomes = []
    for lane, packet in (('native', native), ('legacy', legacy)):
        for index, child_id in enumerate(root_input.ordered_planned_child_cell_ids):
            started = e_donor.time.monotonic()
            case_id = lane + '_child' + str(index)
            e_donor._retained_phase_v06(case_id, 'inputs', 'START', started)
            child = next(c for c in baseline.cell_inputs if c.cell_id == child_id)
            projection = next(p for p in baseline.scope_projections if p.child_cell_id == child_id)
            assert child_id == g2d.derive_fractal_child_cell_id_v02(topology_seed_id=baseline.topology_seed.topology_seed_id,
                parent_cell_id=root_input.cell_id, canonical_child_index=index,
                accepted_mode=baseline.source_binding.accepted_mode,
                selected_local_mode_profile_id=baseline.source_binding.selected_local_mode_profile_id,
                source_mode_profile_set_id=baseline.source_binding.source_mode_profile_set_id,
                child_scope_ref=projection.child_scope_ref, runtime_policy_id=baseline.source_binding.runtime_policy_id,
                required_capability_ids=baseline.source_binding.required_downstream_capability_ids,
                forbidden_claims=baseline.source_context.runtime_policy.forbidden_claims, child_depth=root_input.cell_depth + 1)
            seed = next(a for q, a in zip(baseline.queue_entries, baseline.queue_artifacts)
                if q.queue_entry_id == child.ordered_initial_queue_entry_ids[0])
            fixture = dict(g2a=packet, g2b=g2b, source_family=family, source=family['source'], bundle=baseline,
                selected_seed_projection=e_donor._e4_runtime_artifact_projection(seed))
            inputs = e_donor._e4_input_family(fixture)
            context = inputs['context']
            source_report = g2e.validate_continuous_delta_source_context_v01(context)
            assert source_report.status == 'PASS'
            plan = e_donor._e4_plan_from_inputs(inputs)
            assert plan.ordered_affected_cell_ids == (child_id,)
            assert g2e.validate_selective_recomputation_plan_v01(plan).status == 'PASS'
            e_donor._retained_phase_v06(case_id, 'inputs', 'COMPLETE', started)
            if lane == 'native' and index == 0:
                assert inputs == retained_native_execution_v05['inputs']
                inputs = retained_native_execution_v05['inputs']
                recomputed = retained_native_execution_v05['result']
                validation = retained_native_execution_v05['validation']
            else:
                e_donor._retained_phase_v06(case_id, 'public_E', 'START', started)
                recomputed, validation = g2e.run_continuous_delta_runtime_v01(source_context=context,
                    source_bindings=(inputs['source_binding'],), changed_field_bindings=(inputs['changed_field'],),
                    changed_artifact_bindings=(inputs['changed_artifact'],), delta=inputs['delta'],
                    dependency_edges=inputs['dependency_edges'], dependency_graph=inputs['graph'],
                    retained_profile='fractal_retained_work_v01')
                e_donor._retained_phase_v06(case_id, 'public_E', 'COMPLETE', started)
                print('E_PUBLIC_RETURN_V06=' + json.dumps(actual_evidence_plain_v03(dict(
                    case=case_id, inputs=inputs, result=recomputed, validation=validation)), sort_keys=True), flush=True)
            assert recomputed is not None and validation.status == 'PASS', validation
            row = dict(lane=lane, canonical_index=index, child_id=child_id,
                source_report=g2e.continuous_delta_validation_report_to_plain_data_v01(source_report),
                plan=g2e.selective_recomputation_plan_to_plain_data_v01(plan),
                validation=g2e.continuous_delta_validation_report_to_plain_data_v01(validation), result_present=recomputed is not None)
            if recomputed is not None:
                e_donor._retained_phase_v06(case_id, 'supplied_E', 'START', started)
                checked = (retained_native_execution_v05['supplied_e'] if lane == 'native' and index == 0
                    else g2e.validate_continuous_delta_execution_bundle_v01(recomputed))
                assert checked.status == 'PASS'
                e_donor._retained_phase_v06(case_id, 'supplied_E', 'COMPLETE_SHARED' if lane == 'native' and index == 0 else 'COMPLETE', started)
                retained = recomputed.recomputed_g2d_execution_bundle
                assert type(retained) is g2d.FractalRetainedWorkExecutionBundleV01
                e_donor._retained_phase_v06(case_id, 'supplied_D', 'START', started)
                checked_d = (retained_native_execution_v05['supplied_d'] if lane == 'native' and index == 0
                    else g2d.validate_fractal_retained_work_execution_bundle_v01(retained))
                assert checked_d.status == 'PASS'
                e_donor._retained_phase_v06(case_id, 'supplied_D', 'COMPLETE_SHARED' if lane == 'native' and index == 0 else 'COMPLETE', started)
                row['supplied_e'] = actual_evidence_plain_v03(checked)
                row['supplied_d'] = actual_evidence_plain_v03(checked_d)
                e_donor._retained_phase_v06(case_id, 'relations', 'START', started)
                assert g2d.validate_fractal_runtime_execution_bundle_v02(retained).status == 'FAIL_CLOSED'
                assert len(retained.retained_consumptions) == 1 and len(retained.cell_results) == 2
                consumption = retained.retained_consumptions[0]
                parent_result = next(r for r in retained.cell_results if r.parent_cell_id is None)
                fresh_result = next(r for r in retained.cell_results if r.parent_cell_id is not None)
                assert fresh_result.cell_id == child_id
                assert fresh_result.accepted_output_refs != next(r for r in baseline.cell_results if r.cell_id == child_id).accepted_output_refs
                assert consumption.consumed_result == next(r for r in baseline.cell_results if r.cell_id == consumption.admission.planned_child_cell_id)
                assert consumption.consumed_result not in retained.cell_results
                by_cell = {r.cell_id:r.result_id for r in (fresh_result, consumption.consumed_result)}
                assert parent_result.ordered_child_result_ids == tuple(by_cell[c] for c in root_input.ordered_planned_child_cell_ids)
                assert not any(q.cell_id == consumption.consumed_result.cell_id for q in retained.queue_entries)
                assert recomputed.plan_root_decision_result.decision == recomputed.final_root_decision_result.decision == 'ACCEPT'
                assert recomputed.affected_result == inputs['affected']
                assert recomputed.preservation_proof is not None
                row['preservation'] = g2e.retained_work_preservation_to_plain_data_v01(recomputed.preservation_proof)
                row['runtime_report'] = g2e.continuous_delta_runtime_report_to_plain_data_v01(recomputed.runtime_report)
                row['actual_bundle_report_id'] = recomputed.runtime_report.report_id
                row['complete_body_record'] = 'ACTUAL_RETAINED_NATIVE_V05' if lane == 'native' and index == 0 else 'E_PUBLIC_RETURN_V06:' + case_id
            assert e_donor.canonical_json_bytes_v01(e_donor._e3_public_plain(baseline)) == baseline_bytes
            outcomes.append(row)
            print('E_CANONICAL_PAIR=' + json.dumps(row, sort_keys=True), flush=True)
            e_donor._retained_phase_v06(case_id, 'relations', 'COMPLETE', started)
    started = e_donor.time.monotonic()
    e_donor._retained_phase_v06('M11', 'inputs_and_invalidation', 'START', started)
    context = e_donor._e4_input_family(dict(fixture, g2a=native))['context']
    for bad in (replace(context, g2a_dependency_candidate=runner.prepare_native_playback_v01().root_bound.canonical_projection.dependency_candidate),
        replace(context, g2a_root_invalidation_material=replace(context.g2a_root_invalidation_material, owning_local_root_id='root:foreign')),
        replace(context, baseline_g2c_route_eligibility_artifact=prepared.root_bound),
        replace(context, g2c_source_context=replace(context.g2c_source_context, g2a_evaluation_time=e_donor._E3_TIME+1))):
        assert g2e.validate_continuous_delta_source_context_v01(bad).status == 'FAIL_CLOSED'
    packet_inputs = e_donor._e4_input_family(dict(fixture, g2a=native), target_roles=('packet',))
    assert packet_inputs['invalidation_report'].ordered_packet_invalidation_candidate_ids
    assert g2e.validate_continuous_delta_source_context_v01(packet_inputs['context']).status == 'PASS'
    original = prepared.observations[0]
    changed_envelope = action.build_action_dependency_time_envelope_id_v01(dependency_id=original.dependency_id,
        evidence_ref=original.evidence_ref, content_sha256=native['invalidation'].evidence_sha256,
        freshness_policy_id=original.freshness_policy_id, source_provenance_refs=original.source_provenance_refs,
        valid_from_utc=original.valid_from_utc, valid_to_utc=original.valid_to_utc)
    changed = action.build_action_dependency_current_observation_v01(dependency_id=original.dependency_id,
        evidence_ref=original.evidence_ref, observed_content_sha256=native['invalidation'].evidence_sha256,
        time_envelope_id=changed_envelope, freshness_policy_id=original.freshness_policy_id,
        source_provenance_refs=original.source_provenance_refs, valid_from_utc=original.valid_from_utc,
        valid_to_utc=original.valid_to_utc, observed_at_utc=original.observed_at_utc,
        observation_context_id=original.observation_context_id)
    inspections = []
    inspection_reasons = []
    for observations in (prepared.observations, (changed,)):
        inspection = action.inspect_action_packet_present_eligibility_v01(prepared.registry,
            packet_id=prepared.root_bound.packet_identity.packet_id, corridor=prepared.corridor,
            corridor_step=prepared.corridor_step, current_dependency_observations=observations,
            logical_time_bridge=prepared.bridge, evaluation_time=e_donor._E3_TIME,
            evaluation_time_source='g2e_e3_trusted_ceiling', evaluation_context_id=original.observation_context_id,
            action_packet_transition_registry_profile=transition.build_action_packet_transition_registry_profile_v01())
        inspections.append(inspection.present_executable)
        inspection_reasons.append(inspection.reason_codes)
    assert inspections == [True, False]
    assert inspection_reasons == [(), ('current_dependency_observation_mismatch',)]
    profile = transition.build_action_packet_transition_registry_profile_v01()
    packet_id = prepared.root_bound.packet_identity.packet_id
    before_state = action.derive_action_packet_lifecycle_state_v01(prepared.registry,
        packet_id=packet_id, action_packet_transition_registry_profile=profile)
    assert before_state.lifecycle_state == 'PENDING_FULFILLMENT'
    entry = next(e for e in prepared.registry.action_packet_lifecycle_entries
        if e.root_bound_genesis.packet_identity.packet_id == packet_id)
    last_event = entry.transition_events[-1]
    invalidation = packet_inputs['context'].g2a_root_invalidation_material
    assert invalidation == native['invalidation']
    assert action.validate_action_invalidation_evidence_against_packet_v01(invalidation, prepared.root_bound) == (True, ())
    evidence = (
        ('immediate_eligibility_failure_valid', invalidation.invalidation_evidence_id,
            invalidation.invalidation_evidence_id, action.ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01),
        ('adapter_not_called', last_event.execution_attempt_id,
            last_event.execution_attempt_id[len(action.EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01):],
            action.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01),
        ('idempotency_reservation_owned', before_state.latest_disposition_event_id,
            before_state.latest_disposition_event_id[len(action.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01):],
            action.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01),
    )
    canonical = prepared.root_bound.canonical_projection
    event = action.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,
        transition_rule_id='g2a_t09_pending_block', packet_id=packet_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        previous_transition_event_id=last_event.transition_event_id,
        owning_local_root_id=canonical.owning_local_root_id, root_decision_ref=None,
        transition_evidence_bindings=tuple(action.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=profile, transition_rule_id='g2a_t09_pending_block',
            evidence_code=code, evidence_ref=ref, evidence_sha256=sha, validator_profile_id=validator)
            for code, ref, sha, validator in evidence),
        dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,
        temporal_authority_fingerprint=canonical.temporal_authority_fingerprint,
        evaluation_time=invalidation.evaluation_time, evaluation_time_source=invalidation.evaluation_time_source,
        evaluation_context_id=invalidation.evaluation_context_id, execution_attempt_identity=None, receipt_ref=None)
    blocked = action.record_action_packet_deterministic_invalidation_v01(prepared.registry,
        packet_id=packet_id, invalidation_evidence=invalidation, transition_event=event,
        action_packet_transition_registry_profile=profile)
    after_state = action.derive_action_packet_lifecycle_state_v01(blocked,
        packet_id=packet_id, action_packet_transition_registry_profile=profile)
    assert after_state.lifecycle_state == 'BLOCKED' and not after_state.executable
    assert blocked.idempotency_disposition_events is prepared.registry.idempotency_disposition_events
    assert action.validate_action_commit_packet_registry_v02(blocked) == (True, ())
    print('M11_ACTUAL_APPLIED_INVALIDATION=' + json.dumps(actual_evidence_plain_v03(dict(
        before=before_state, after=after_state, event=event, registry=blocked,
        invalidation=invalidation)), sort_keys=True), flush=True)
    captured = []
    def observe_return(code, offset, value):
        if type(value) is g2d.FractalRuntimeExecutionBundleV02:
            captured.append(value)
    tool = next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
    observed_code = g2d.build_fractal_runtime_execution_bundle_v02.__code__
    sys.monitoring.use_tool_id(tool, 'read_only_actual_packet_D_return')
    sys.monitoring.register_callback(tool, sys.monitoring.events.PY_RETURN, observe_return)
    sys.monitoring.set_local_events(tool, observed_code, sys.monitoring.events.PY_RETURN)
    e_donor._retained_phase_v06('M11', 'legacy_public_E', 'START', started)
    try:
        packet_result, packet_validation = g2e.run_continuous_delta_runtime_v01(source_context=packet_inputs['context'],
            source_bindings=(packet_inputs['source_binding'],), changed_field_bindings=(packet_inputs['changed_field'],),
            changed_artifact_bindings=(packet_inputs['changed_artifact'],), delta=packet_inputs['delta'],
            dependency_edges=packet_inputs['dependency_edges'], dependency_graph=packet_inputs['graph'])
    finally:
        sys.monitoring.set_local_events(tool, observed_code, 0)
        sys.monitoring.register_callback(tool, sys.monitoring.events.PY_RETURN, None)
        sys.monitoring.free_tool_id(tool)
    assert len(captured) == 1
    blocked_d = captured[0]
    assert g2d.validate_fractal_runtime_execution_bundle_v02(blocked_d).status == 'PASS'
    # This actual negative establishes source binding, not a completion branch.
    case = exact_review_cases[0]
    assert check_exact_review(case) == (True, ())
    assert blocked_d.source_context != case['source']
    rejected = check_exact_review(case, bundle=blocked_d)
    assert rejected == (False, ('work_review_bundle_source',))
    print('D_ACTUAL_BLOCKED_REVIEW=' + json.dumps(dict(runtime_report=g2d.fractal_runtime_report_to_plain_data_v02(
        blocked_d.runtime_report), review_result=rejected, positive_control=True,
        coverage='ACTUAL_WORK_SOURCE_BINDING_NOT_COMPLETION_BRANCH'), sort_keys=True), flush=True)
    assert packet_result is None and packet_validation.status == 'FAIL_CLOSED'
    assert packet_validation.failure_stage == 'bundle_final'
    assert packet_validation.reason_codes == ('g2e_recomputation_no_progress', 'g2e_transition_selective_recomputation_blocked')
    print('LEGACY_PACKET_PREFIX_REFUSAL=' + json.dumps(actual_evidence_plain_v03(packet_validation)), flush=True)
    e_donor._retained_phase_v06('M11', 'legacy_public_E', 'COMPLETE_INTENDED_REFUSAL', started)
    e_donor._retained_phase_v06('M11', 'retained_public_E', 'START', started)
    packet_result, packet_validation = g2e.run_continuous_delta_runtime_v01(source_context=packet_inputs['context'],
        source_bindings=(packet_inputs['source_binding'],), changed_field_bindings=(packet_inputs['changed_field'],),
        changed_artifact_bindings=(packet_inputs['changed_artifact'],), delta=packet_inputs['delta'],
        dependency_edges=packet_inputs['dependency_edges'], dependency_graph=packet_inputs['graph'],
        retained_profile='fractal_retained_work_v01')
    assert packet_result is not None and packet_validation.status == 'PASS', packet_validation
    assert packet_result.affected_result == packet_inputs['affected']
    assert packet_result.final_root_decision_result.decision == 'ACCEPT'
    print('ACTUAL_M11_FULL_RESULT=' + json.dumps(actual_evidence_plain_v03(dict(
        inputs=packet_inputs, result=packet_result, validation=packet_validation)), sort_keys=True), flush=True)
    e_donor._retained_phase_v06('M11', 'retained_public_E', 'COMPLETE', started)
    e_donor._retained_phase_v06('M11', 'supplied_E', 'START', started)
    packet_checked_e = g2e.validate_continuous_delta_execution_bundle_v01(packet_result)
    assert packet_checked_e.status == 'PASS'
    e_donor._retained_phase_v06('M11', 'supplied_E', 'COMPLETE', started)
    e_donor._retained_phase_v06('M11', 'supplied_D', 'START', started)
    packet_checked_d = g2d.validate_fractal_retained_work_execution_bundle_v01(packet_result.recomputed_g2d_execution_bundle)
    assert packet_checked_d.status == 'PASS'
    e_donor._retained_phase_v06('M11', 'supplied_D', 'COMPLETE', started)
    print('E_NATIVE_PACKET_DEPENDENCY=' + json.dumps(dict(
        affected=g2e.affected_set_result_to_plain_data_v01(packet_inputs['affected']),
        invalidation=g2e.invalidation_report_to_plain_data_v01(packet_inputs['invalidation_report']),
        eligibility_before_after=inspections, eligibility_reasons=inspection_reasons,
        validation=g2e.continuous_delta_validation_report_to_plain_data_v01(packet_validation),
        supplied_e=actual_evidence_plain_v03(packet_checked_e), supplied_d=actual_evidence_plain_v03(packet_checked_d),
        result_present=packet_result is not None), sort_keys=True), flush=True)
    e_donor._retained_phase_v06('M11', 'relations', 'COMPLETE', started)
    assert all(row['validation']['status'] == 'PASS' and row['result_present'] for row in outcomes), [
        (r['lane'], r['canonical_index'], r['validation']['status'], r['validation']['reason_codes']) for r in outcomes]


def test_work_coherent_changed_input_and_source_require_their_actual_review(exact_review_cases):
    left, right = exact_review_cases
    assert left['source'].decision.accepted_scope_ref != right['source'].decision.accepted_scope_ref
    for case in (left, right):
        assert g2d.validate_fractal_runtime_execution_bundle_v02(case['bundle']).status == 'PASS'
        assert check_exact_review(case) == (True, ())
    altered, old_obligation = attach_review(right['program'], right['common'], left['source'])
    rejected = check_exact_review(right, program=altered, obligation=old_obligation,
        source=left['source'], bundle=left['bundle'])
    assert rejected == (False, ('work_review_exact_scope',))
    assert not check_exact_review(right, bundle=left['bundle'])[0]
    for changes in ({'work_id': 'reviewed_other'}, {'semantic_suffix': ':different'},
        {'task_id': 'task:composition:foreign'}, {'root_id': 'root:composition:foreign'}):
        p, c, _ = prepare_exact_review_work(19, **changes)
        p, obligation = attach_review(p, c, left['source'])
        result = work.validate_work_review_binding_v01(obligation, candidate=p.candidate, item=p.candidate.items[0],
            source_context=left['source'], execution_bundle=left['bundle'], semantic_proposal=c['semantic_proposal'])
        assert not result[0]
    old_semantic = left['common']['semantic_proposal']
    plain = abi.kernel_artifact_to_plain_dict_v01(old_semantic)
    changed_semantic = abi.build_kernel_artifact_v01(**dict(plain, payload={'bounded_work_ids': ['changed_semantics']},
        trace_refs=tuple(plain['trace_refs']), parent_refs=tuple(plain['parent_refs'])))
    assert check_exact_review(left, semantic=changed_semantic) == (False, ('work_review_exact_scope',))
    program, common, host = (right[k] for k in ('program','common','host'))
    result = work.advance_work_program_v01(program, **common, host_map={host.owning_root_id: host},
        review_bindings=((right['obligation'], right['source'], right['bundle']),))
    assert result[0].status == 'COMPLETED' and result[0].result.output[0].value == 23
    right['completed_results'] = result
    print('COHERENT_CHANGED_REVIEW=' + json.dumps(dict(old_scope=left['source'].decision.accepted_scope_ref,
        new_scope=right['source'].decision.accepted_scope_ref, rejection=rejected, actual_new_output=result[0].result.output[0].value),
        sort_keys=True), flush=True)


def test_work_review_commitment_includes_dependencies_guard_budget_and_sources():
    p, c, _ = runner.prepare_alarm_program_v01()
    item = p.candidate.items[-1]
    def scope(program, common=c):
        return work.build_work_review_scope_ref_v01(candidate=program.candidate, item=program.candidate.items[-1],
            source_context=common['source_context'], semantic_proposal=common['semantic_proposal'])
    original = scope(p)
    new_parent = replace(p.candidate.items[0], inputs=(runner.work_literal_v01('reading','INTEGER',99),))
    for changes in (dict(items=(new_parent,*p.candidate.items[1:])),
        dict(items=(*p.candidate.items[:-1],replace(item,guard=None))),
        dict(budget=replace(p.candidate.budget,max_compute_units=17)),
        dict(trigger_evidence_refs=('evidence:changed',))):
        altered = rebuild_program(p,c,**changes)
        assert scope(altered) != original
    reordered = rebuild_program(p,c,items=tuple(reversed(p.candidate.items)))
    same_item = next(i for i in reordered.candidate.items if i.work_id == item.work_id)
    assert reordered.candidate.revision_id != p.candidate.revision_id
    assert work.build_work_review_scope_ref_v01(candidate=reordered.candidate,item=same_item,
        source_context=c['source_context'],semantic_proposal=c['semantic_proposal']) == original
    with pytest.raises(ValueError,match='work_semantic_binding'):
        rebuild_program(p,c,intent_ref='intent:other')


def test_work_actual_blocked_review_cannot_authorize_dispatch(exact_review_cases):
    p,c,h = prepare_exact_review_work()
    arguments,rejected_common = build_exact_review_source(p,c,blocked=True)
    assert rejected_common['semantic_proposal'] == c['semantic_proposal']
    # Actual Root REJECT has no route artifact; it cannot construct an accepted
    # D source. This is not a fabricated non-COMPLETED execution bundle.
    with pytest.raises(ValueError, match='^g2d_route_eligibility_missing$'):
        g2d.build_fractal_runtime_source_context_v02(**arguments)
    rejected_source = g2d.FractalRuntimeSourceContextV02(**arguments)
    bundle,report = g2d.run_fractal_runtime_v02(rejected_source)
    assert bundle is None and report.status == 'FAIL_CLOSED'
    assert report.reason_codes == ('g2d_route_eligibility_missing',)
    case = exact_review_cases[0]
    c = dict(c,source_context=case['source'].g2c_source_context)
    assert c['catalogue'][0] is h.admitted_catalogue[0]
    assert c['catalogue'][0].definition == case['common']['catalogue'][0].definition
    p,obligation = attach_review(p,c,case['source'])
    results = work.advance_work_program_v01(p,**c,host_map={h.owning_root_id:h})
    assert results[0].status == 'BLOCKED_INVALID_INPUT' and h.events == () and h.work_attempts == ()
    assert results[0].reasons == ('work_required_review_missing',)
    accepted = work.advance_work_program_v01(p,**c,host_map={h.owning_root_id:h},results=results,
        review_bindings=((obligation,case['source'],case['bundle']),))
    assert accepted[0].status == 'COMPLETED' and accepted[0].result.output[0].value == 19
    print('ACTUAL_BLOCKED_REVIEW=' + json.dumps(dict(boundary='ROOT_REJECTED_BEFORE_D',
        root_decision=g2c.root_execution_mode_decision_to_plain_data_v01(arguments['decision']),
        rejection=g2d.fractal_runtime_validation_report_to_plain_data_v02(report),
        no_bundle=True,no_dispatch_before_matching_review=True,proper_control_output=accepted[0].result.output[0].value),sort_keys=True),flush=True)


def test_work_genuine_foreign_root_candidate_and_corridor_refused_before_install():
    setups = []
    for root in ('root:composition:cross_left','root:composition:cross_right'):
        p,c,h = runner.prepare_content_program_v01(root_id=root)
        results = work.advance_work_program_v01(p,**c,host_map={root:h})
        assert results[-1].status == 'READY' and h.registry.action_packet_lifecycle_entries == ()
        item = p.candidate.items[-1]
        inputs = (action.build_action_effect_parameter_record_v01(parameter_name='content_ref',value_type='REFERENCE',
            value=results[1].result.output[0].value), action.build_action_effect_parameter_record_v01(
            parameter_name='device_ref',value_type='REFERENCE',value=item.resource_refs[0]))
        auth = runner.authorize_resolved_work_v01(p.candidate,item,inputs,c['catalogue'][-1])
        assert action.validate_native_root_bound_action_commit_packet_v01(auth['root_bound']) == (True,())
        setups.append((p,c,h,results,inputs,auth))
    left,right = setups
    p,c,h,results,inputs,auth = left
    before=(h.registry,h.events,h.work_attempts,h.state_revision)
    clock=h.current_sources
    args=dict(admission_id=c['catalogue'][-1].admission_id,inputs=inputs,expected_revision=h.state_revision,
        evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,
        evaluation_context_id=clock.evaluation_context_id)
    with pytest.raises(ValueError,match='^host_foreign_root$'):
        hosts.install_current_action_v01(h,**right[5],**args)
    assert (h.registry,h.events,h.work_attempts,h.state_revision)==before
    with pytest.raises(ValueError,match='^host_installed_action_not_current$'):
        hosts.install_current_action_v01(h,**dict(auth,corridor=right[5]['corridor'],corridor_step=right[5]['corridor_step']),**args)
    assert (h.registry,h.events,h.work_attempts,h.state_revision)==before
    refusal=action.validate_common_root_context_coherence_v01(right[5]['root_bound'].root_decision_projection,
        auth['root_bound'].canonical_projection)
    assert refusal == (False, ('supplier_root_context_candidate_mismatch',
        'supplier_root_context_root_mismatch', 'supplier_root_context_permission_mismatch',
        'supplier_root_context_policy_mismatch'))
    positives=[]
    for p,c,h,prior,inputs,auth in setups:
        clock=h.current_sources
        packet,revision=hosts.install_current_action_v01(h,**auth,admission_id=c['catalogue'][-1].admission_id,
            inputs=inputs,expected_revision=h.state_revision,evaluation_time=clock.evaluation_time,
            evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
        registry,_=hosts.dispatch_current_action_v01(h,packet_id=packet,task_id=p.candidate.task_id,expected_revision=revision,
            evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,
            evaluation_context_id=clock.evaluation_context_id)
        assert registry.action_packet_fulfillment_attempt_contexts[-1].receipt is not None
        assert len(registry.action_packet_lifecycle_entries)==1
        positives.append(dict(root=h.owning_root_id,packet=packet,
            permission=auth['root_bound'].canonical_projection.canonical_permission_ref,
            root_bound=actual_evidence_plain_v03(auth['root_bound']),
            corridor=actual_evidence_plain_v03(auth['corridor']),
            corridor_step=actual_evidence_plain_v03(auth['corridor_step']),
            receipt=abi.kernel_artifact_to_plain_dict_v01(registry.action_packet_fulfillment_attempt_contexts[-1].receipt)))
    print('GENUINE_CROSS_ROOT_CONTROL=' + json.dumps(dict(positives=positives,
        foreign_candidate='host_foreign_root',foreign_corridor='host_installed_action_not_current',
        root_projection_refusal=refusal,preinstall_state_unchanged=True),sort_keys=True),flush=True)


# Test-only shared actual public native execution, not a production cache.
retained_native_execution_v05 = e_donor.retained_native_execution_v05


def u2_setup(content='content:u2:cedar', *, task_id='task:u2:continuation', initial_effect=False,
    compute=8, children=24, uncertain=False, with_review=False):
    root, device = 'root:u2:local', 'device:u2:local'
    host_ref = 'host:' + root
    first = mocks.admit_pure_operation_v01(operation_id='u2.property', input_fields=(('property', 'REFERENCE'),),
        output_fields=(('content_ref', 'REFERENCE'),), executor=mocks.read_property_v01,
        output_validator=mocks.validate_property_output_v01, host_instance_ref=host_ref)
    second = mocks.admit_pure_operation_v01(operation_id='u2.transform', input_fields=(('content_ref', 'REFERENCE'),),
        output_fields=(('transformed_ref', 'REFERENCE'),), executor=mocks.transform_content_v01,
        output_validator=mocks.validate_transform_output_v01, host_instance_ref=host_ref)
    effect = mocks.admit_playback_v01(device, host_ref)
    if uncertain:
        effect = mocks.admit_playback_variant_v01(device, host_ref, mocks.execute_playback_uncertain_v01)
    catalogue = (first, second, effect)
    item = work.WorkItemV01('original_read', first.definition.definition_id, root,
        (runner.work_literal_v01('property', 'REFERENCE', content),), (), (), None, None)
    items = (item,)
    if initial_effect:
        items += (work.WorkItemV01('original_effect', effect.definition.definition_id, root,
            (work.WorkInputBindingV01('content_ref', work.WorkOutputBindingV01(item.work_id, 'content_ref', 'REFERENCE')),
             runner.work_literal_v01('device_ref', 'REFERENCE', device)), (device,), (item.work_id,), None, None),)
    source = mocks.build_work_source_context_v01(task_id)
    semantic = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='semantic:' + task_id,
        artifact_type='SemanticArchitectProposal', schema_version='v1', transaction_id='transaction:' + task_id,
        owner_root_id=root, source_component='semantic_architect', authority_class='ADVISORY', lifecycle_state='PROPOSED',
        payload={'intent': 'bounded continuation from observed content', 'provenance': 'CONTROLLED_PROPOSER'},
        trace_refs=('intent:' + task_id,), parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope={'pt_created_at': '2026-01-01T00:00:00+00:00', 'kt_asof': '2026-01-01T00:00:00+00:00',
            'et_observed_at': None, 'ct_session_anchor': 'session:' + task_id, 'ttl_seconds': 3600,
            'freshness_class': 'static', 'valid_from': '2026-01-01T00:00:00+00:00', 'valid_to': '2026-01-01T01:00:00+00:00'})
    common = dict(catalogue=catalogue, source_context=source, semantic_proposal=semantic)
    candidate = work.build_work_program_candidate_v01(task_id=task_id, previous_revision_id=None, intent_ref='intent:' + task_id,
        bsep_ref=source.bsep_packet['packet_id'], semantic_proposal_ref=semantic.artifact_id, catalogue_revision=0,
        budget=work.WorkBudgetV01(8, children, 0, compute, 2), items=items, trigger_evidence_refs=(), **common)
    program = work.materialize_work_program_v01(candidate, **common)
    review_source = obligation = None
    if with_review:
        review_source, common = build_exact_review_source(program, common)
        program, obligation = attach_review(program, common, review_source)
    policy = work.build_work_task_policy_v01(program.candidate, **common, host_instance_ref=host_ref,
        definition_ids=tuple(sorted([a.definition.definition_id for a in catalogue] + ['definition:u2:unavailable'])),
        resource_refs=(device,))
    observations = (runner.build_work_dependency_v01(device, root)[2],)
    bridge = action.build_logical_time_bridge_v01(origin_utc_epoch_seconds=1000, seconds_per_tick=1,
        bridge_policy_version='u1.controlled_ticks.v01')
    trusted = mocks.TrustedMockWorkSourceV01(observations, bridge, 1014, 'u1.controlled_utc', 'context:u1:dispatch')
    host = hosts.build_root_work_execution_host_v01(owning_root_id=root,
        registry=action.build_empty_action_commit_packet_registry_v02(), catalogue=catalogue, packet_bindings=(),
        current_dependency_observations=observations, logical_time_bridge=bridge, trusted_source=trusted, task_policies=(policy,))
    context = work.enroll_work_program_v01(host, program, **common, expected_revision=host.state_revision)
    return dict(host=host, program=program, common=common, context=context, device=device,
        review_source=review_source, obligation=obligation)


def u2_context(case):
    return work.work_continuation_context_v01(case['host'], task_id=case['program'].candidate.task_id,
        expected_revision=case['host'].state_revision)


def u2_advance(case, outcome=None, *, authorizer=runner.authorize_resolved_work_v01, review_bindings=()):
    program = case['program'] if outcome is None else outcome.program
    results = () if outcome is None else outcome.results
    result = work.advance_work_program_v01(program, **case['common'], host_map={case['host'].owning_root_id: case['host']},
        results=results, continuation_context=u2_context(case), review_bindings=review_bindings,
        action_authorizers={} if authorizer is None else {case['host'].owning_root_id: authorizer})
    assert work.validate_work_continuation_outcome_v01(result, context=u2_context(case),
        **case['common'], review_bindings=review_bindings) == (True, ())
    return result


def u2_controlled_proposal(trigger, catalogue, root, device, ordinal):
    """Data-only proposer executed after a genuine intermediate result exists."""
    assert type(trigger) is work.WorkRevisionTriggerV01 and trigger.output.value.value_type == 'REFERENCE'
    actual = trigger.output.value.value
    assert type(actual) is str
    suffix = hashlib.sha256(actual.encode()).hexdigest()[:12]
    transform_id = 'transform:' + str(ordinal) + ':' + suffix
    effect_id = 'effect:' + str(ordinal) + ':' + suffix
    transform = work.WorkItemV01(transform_id, catalogue[1].definition.definition_id, root,
        (work.WorkInputBindingV01('content_ref', trigger.output),), (), (), None, None)
    effect = work.WorkItemV01(effect_id, catalogue[2].definition.definition_id, root,
        (work.WorkInputBindingV01('content_ref', work.WorkOutputBindingV01(transform_id, 'transformed_ref', 'REFERENCE')),
         runner.work_literal_v01('device_ref', 'REFERENCE', device)), (device,), (transform_id,), None, None)
    return transform, effect


def u2_revise(case, prior, *, trigger=None, items=None, budget=None, context=None):
    context = u2_context(case) if context is None else context
    if trigger is None:
        value = next(r for r in reversed(prior.results) if r.status == 'COMPLETED')
        field = 'content_ref' if any(v.parameter_name == 'content_ref' for v in value.result.output) else 'transformed_ref'
        trigger = work.build_work_revision_trigger_v01(context, work_id=value.work_id, output_field=field)
    items = u2_controlled_proposal(trigger, case['common']['catalogue'], case['host'].owning_root_id,
        case['device'], context.snapshot.usage.revisions + 1) if items is None else items
    state = context.snapshot
    if budget is None:
        budget = work.WorkBudgetV01(state.policy.max_items, state.policy.max_children - state.usage.children - state.usage.reserved_children,
            0, state.policy.max_compute_units - state.usage.compute_units, max(0, state.policy.max_revisions - state.usage.revisions - 1))
    result = work.revise_work_program_v01(context, previous_revision_id=prior.program.candidate.revision_id,
        trigger=trigger, items=items, budget=budget, **case['common'])
    return result, trigger


def u2_emit(case_id, **values):
    print('U2_CASE=' + json.dumps(dict(case_id=case_id, **{k: actual_evidence_plain_v03(v) for k, v in values.items()}),
        sort_keys=True), flush=True)


def test_u2_r01_actual_two_revisions_and_counterfactual():
    final_values = []
    for content in ('content:u2:cedar', 'content:u2:birch'):
        case = u2_setup(content)
        initial = u2_advance(case)
        assert initial.status == 'COMPLETED' and initial.snapshot.usage.compute_units == 1
        first, trigger1 = u2_revise(case, initial)
        assert first.program.candidate.previous_revision_id == initial.program.candidate.revision_id
        first = u2_advance(case, first)
        assert first.status == 'COMPLETED'
        second, trigger2 = u2_revise(case, first)
        second = u2_advance(case, second)
        assert second.status == 'COMPLETED' and second.snapshot.usage == hosts.WorkTaskUsageV01(5, 0, 0, 2, 0)
        actual = {v.parameter_name: v.value for v in second.results[-1].result.output}
        assert actual['content_ref'] == content + ':rendered:rendered'
        assert second.results[0].invocation.inputs[0].value == trigger2.output.value.value
        assert second.results[0].consumed_fields[0].source_artifact_id == trigger2.output.result_id
        assert second.results[0].consumed_fields[0].trace_refs[2] == first.program.candidate.revision_id
        entries = case['host'].registry.action_packet_lifecycle_entries
        assert len(entries) == 2
        assert len({e.root_bound_genesis.root_decision_projection.root_decision_result.decision_id for e in entries}) == 2
        assert all(e.root_bound_genesis.root_decision_projection.root_decision_result.decision == 'ACCEPT' for e in entries)
        history = work.inspect_work_task_history_v01(u2_context(case))
        assert history[0][1] == initial.results and history[1][1] == first.results
        before = case['host'].events, case['host'].work_attempts, mocks.observed_mock_calls_v01()
        assert u2_advance(case, second) == second
        assert (case['host'].events, case['host'].work_attempts, mocks.observed_mock_calls_v01()) == before
        exhausted, trigger3 = u2_revise(case, second)
        assert exhausted.status == 'EXHAUSTED' and exhausted.reason == 'work_task_revision_exhausted'
        assert exhausted.snapshot.usage == second.snapshot.usage and case['host'].work_attempts == before[1]
        final_values.append((actual, second.program.candidate.items[0].work_id))
        u2_emit('R01_TWO_REVISIONS.' + content, initial=initial, trigger1=trigger1, first=first, trigger2=trigger2,
            second=second, trigger3=trigger3, exhausted=exhausted, history=history, events=case['host'].events,
            registry=case['host'].registry, source=case['common']['source_context'], semantic=case['common']['semantic_proposal'],
            proposer='CONTROLLED_PROPOSER', model_calls=0, real_adapter_calls=0)
    assert final_values[0] != final_values[1]


def test_u2_r01_coherent_trigger_context_scope_and_graph_controls():
    case = u2_setup()
    initial = u2_advance(case)
    context = u2_context(case)
    trigger = work.build_work_revision_trigger_v01(context, work_id='original_read', output_field='content_ref')
    items = u2_controlled_proposal(trigger, case['common']['catalogue'], case['host'].owning_root_id, case['device'], 1)
    budget = work.WorkBudgetV01(8, 24, 0, 7, 1)
    base = dict(previous_revision_id=initial.program.candidate.revision_id, trigger=trigger, items=items, budget=budget, **case['common'])
    before = case['host'].events, case['host'].work_attempts, context.snapshot
    bad_field = action.build_action_effect_parameter_record_v01(parameter_name='content_ref', value_type='REFERENCE', value='content:not_observed')
    output = replace(trigger.output, value=bad_field)
    material = json.dumps(actual_evidence_plain_v03(output), sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    forged = work.WorkRevisionTriggerV01(action.build_domain_separated_identity_v01(domain='hedgehog.common_action.work_revision_trigger.v01',
        prefix='work_revision_trigger:', material=(('payload', material),)), output)
    cases = (
        ('missing_trigger', dict(trigger=None), 'work_task_trigger_required'),
        ('coherent_unobserved_field', dict(trigger=forged), 'work_historical_actual_field'),
        ('historical_type', dict(items=(replace(items[0], inputs=(work.WorkInputBindingV01('content_ref',
            replace(trigger.output, expected_type='TEXT')),)), items[1])), 'work_historical_actual_field'),
        ('wrong_predecessor', dict(previous_revision_id='revision:foreign'), 'work_task_predecessor'),
        ('cycle', dict(items=(replace(items[0], depends_on=(items[1].work_id,)), items[1])), 'work_cycle'),
        ('foreign_root', dict(items=(replace(items[0], owning_root_id='root:foreign'), items[1])), 'work_task_original_scope'),
        ('foreign_target', dict(items=(items[0], replace(items[1], resource_refs=('device:foreign',)))), 'work_task_original_scope'),
        ('remaining_compute', dict(budget=replace(budget, max_compute_units=8)), 'work_task_remaining_budget'),
        ('remaining_revisions', dict(budget=replace(budget, max_revisions=2)), 'work_task_remaining_budget'),
        ('model_credit', dict(budget=replace(budget, max_model_calls=1)), 'work_task_original_budget'),
        ('missing_semantic', dict(semantic_proposal=None), 'work_task_original_context'),
    )
    for name, changes, reason in cases:
        with pytest.raises(ValueError, match='^' + reason + '$') as caught:
            work.revise_work_program_v01(context, **dict(base, **changes))
        assert (case['host'].events, case['host'].work_attempts, u2_context(case).snapshot) == before
        u2_emit('R01_NEGATIVE.' + name, observed_reason=str(caught.value), executor_attempts=len(case['host'].work_attempts))
    for snapshot in (replace(context.snapshot, terminal_history_refs=()), replace(context.snapshot, host_revision=0),
        replace(context.snapshot, usage=replace(context.snapshot.usage, compute_units=0))):
        with pytest.raises(ValueError, match='^work_task_stale_snapshot$'):
            work.revise_work_program_v01(replace(context, snapshot=snapshot), **base)
    equivalent = replace(trigger, output=replace(trigger.output, value=action.build_action_effect_parameter_record_v01(
        parameter_name=trigger.output.value.parameter_name, value_type=trigger.output.value.value_type, value=trigger.output.value.value)))
    assert equivalent == trigger and equivalent is not trigger
    accepted = work.revise_work_program_v01(context, **dict(base, trigger=equivalent))
    assert accepted.status == 'ACTIVE'
    with pytest.raises(ValueError, match='^work_task_stale_snapshot$'):
        work.revise_work_program_v01(context, **base)
    with pytest.raises(ValueError, match='^work_task_context_required$'):
        work.advance_work_program_v01(initial.program, **case['common'], host_map={case['host'].owning_root_id: case['host']})
    with pytest.raises(ValueError, match='^work_task_history_omitted$'):
        work.advance_work_program_v01(accepted.program, **case['common'], host_map={case['host'].owning_root_id: case['host']},
            continuation_context=u2_context(case), results=initial.results)
    assert len(case['host'].work_attempts) == 1
    u2_emit('R01_EQUIVALENT_CONTROL', accepted=accepted, trigger=equivalent)


def test_u2_r02_compute_exhaustion_and_unknown_capability():
    case = u2_setup(compute=1)
    completed = u2_advance(case)
    before = case['host'].work_attempts, mocks.observed_mock_calls_v01()
    exhausted, _ = u2_revise(case, completed)
    assert exhausted.status == 'EXHAUSTED' and exhausted.reason == 'work_task_compute_exhausted'
    assert exhausted.snapshot.usage.compute_units == 1
    assert (case['host'].work_attempts, mocks.observed_mock_calls_v01()) == before
    assert work.validate_work_continuation_outcome_v01(exhausted, context=u2_context(case), **case['common']) == (True, ())
    u2_emit('R02_COMPUTE_EXHAUSTED', outcome=exhausted, events=case['host'].events)
    other = u2_setup(task_id='task:u2:missing')
    initial = u2_advance(other)
    trigger = work.build_work_revision_trigger_v01(u2_context(other), work_id='original_read', output_field='content_ref')
    missing = work.WorkItemV01('missing', 'definition:u2:unavailable', other['host'].owning_root_id,
        (work.WorkInputBindingV01('content_ref', trigger.output),), (), (), None, None)
    revised, _ = u2_revise(other, initial, trigger=trigger, items=(missing,))
    before = other['host'].work_attempts
    result = u2_advance(other, revised)
    assert result.status == 'NEEDS_CAPABILITY' and result.results[0].status == 'NEEDS_CAPABILITY'
    assert other['host'].work_attempts == before and result.snapshot.usage.compute_units == 1
    u2_emit('R01_NEEDS_CAPABILITY', outcome=result)


def test_u2_r03_prior_effect_and_history_never_replayed():
    case = u2_setup(initial_effect=True)
    initial = u2_advance(case)
    effect = next(v for v in initial.results if v.work_id == 'original_effect')
    assert effect.status == 'COMPLETED'
    packet = effect.invocation.packet_id
    original_context = case['host'].registry.action_packet_fulfillment_attempt_contexts[0]
    old_bytes = json.dumps(actual_evidence_plain_v03(original_context), sort_keys=True)
    original_attempts = case['host'].work_attempts
    calls_before = [c for c in mocks.observed_mock_calls_v01() if c[0] == 'EXECUTOR_STARTED' and c[1] == effect.invocation.invocation_id]
    assert len(calls_before) == 1
    first, trigger = u2_revise(case, initial)
    assert trigger.output.result_id == effect.result.result_id and trigger.output.revision_id == initial.program.candidate.revision_id
    first = u2_advance(case, first)
    second, _ = u2_revise(case, first)
    second = u2_advance(case, second)
    assert second.status == 'COMPLETED'
    assert json.dumps(actual_evidence_plain_v03(case['host'].registry.action_packet_fulfillment_attempt_contexts[0]), sort_keys=True) == old_bytes
    assert case['host'].work_attempts[:len(original_attempts)] == original_attempts
    before = mocks.observed_mock_calls_v01()
    replay = case['host'].replay(packet_id=packet)
    assert not replay.reconstructed_state.executable
    history = work.inspect_work_task_history_v01(u2_context(case))
    assert history[0][1] == initial.results and history[0][1][1] is effect
    assert u2_advance(case, second) == second
    assert mocks.observed_mock_calls_v01() == before
    assert sum(c[0] == 'EXECUTOR_STARTED' and c[1] == effect.invocation.invocation_id for c in before) == 1
    u2_emit('R03_ORIGINAL_EFFECT', initial=initial, first=first, second=second, original_context=original_context,
        replay=replay, original_attempts=original_attempts, current_attempts=case['host'].work_attempts)


def test_u2_r03_pending_revocation_and_same_time_current_positive():
    outcomes = []
    for revoke in (True, False):
        case = u2_setup(task_id='task:u2:pending')
        initial = u2_advance(case)
        revised, trigger = u2_revise(case, initial)
        pending_result = u2_advance(case, revised, authorizer=None)
        assert tuple(r.status for r in pending_result.results) == ('COMPLETED', 'READY')
        item = pending_result.program.candidate.items[-1]
        value = pending_result.results[0].result.output[0]
        inputs = (action.build_action_effect_parameter_record_v01(parameter_name='content_ref', value_type='REFERENCE', value=value.value),
            action.build_action_effect_parameter_record_v01(parameter_name='device_ref', value_type='REFERENCE', value=case['device']))
        admitted = case['common']['catalogue'][2]
        canonical = runner.build_native_work_action_v01(admitted=admitted, inputs=inputs, root_id=case['host'].owning_root_id,
            transaction_id=case['common']['semantic_proposal'].transaction_id, business_object_ref=value.value)
        prepared = runner.authorize_and_prepare_action_v01(canonical, admitted, inputs)
        auth = dict(root_bound=prepared.root_bound, corridor=prepared.corridor, corridor_step=prepared.corridor_step,
            transition_events=prepared.registry.action_packet_lifecycle_entries[0].transition_events,
            disposition_event=prepared.registry.idempotency_disposition_events[0])
        pending = work.prepare_work_task_action_v01(u2_context(case), work_id=item.work_id, authorization=auth, **case['common'])
        assert pending.inputs == inputs and pending.revision_id == revised.program.candidate.revision_id
        assert canonical.temporal_authority.expires_at_utc > case['host'].current_sources.evaluation_time == 1014
        assert action.derive_action_packet_lifecycle_state_v01(case['host'].registry, packet_id=pending.packet_id).lifecycle_state == 'PENDING_FULFILLMENT'
        stale = u2_context(case)
        calls = mocks.observed_mock_calls_v01()
        if revoke:
            revocation = runner.build_prestart_root_revocation_v01(prepared)
            assert revocation['revocation_root_projection'].root_decision_result.decision == 'ACCEPT'
            registry, revision = hosts.accept_current_revocation_v01(case['host'], expected_revision=case['host'].state_revision, **revocation)
            assert registry is case['host'].registry and revision == case['host'].state_revision
            with pytest.raises(ValueError, match='^work_task_stale_snapshot$'):
                work.advance_work_program_v01(pending_result.program, **case['common'], host_map={case['host'].owning_root_id: case['host']},
                    results=pending_result.results, continuation_context=stale)
            with pytest.raises(ValueError, match='^host_current_action_not_executable$') as caught:
                u2_advance(case, pending_result, authorizer=None)
            assert mocks.observed_mock_calls_v01() == calls
            assert action.derive_action_packet_lifecycle_state_v01(case['host'].registry, packet_id=pending.packet_id).lifecycle_state == 'REVOKED'
            assert len(case['host'].work_attempts) == 2
            u2_emit('R03_PRESTART_REVOKE', pending=pending, trigger=trigger, revocation=revocation,
                actual_reason=str(caught.value), registry=registry, events=case['host'].events, executor_delta=0)
            outcomes.append('REVOKED')
        else:
            completed = u2_advance(case, pending_result, authorizer=None)
            assert completed.status == 'COMPLETED' and completed.results[-1].invocation.packet_id == pending.packet_id
            assert sum(c[0] == 'EXECUTOR_STARTED' for c in mocks.observed_mock_calls_v01()[len(calls):]) == 1
            u2_emit('R03_SAME_TIME_POSITIVE', pending=pending, completed=completed, registry=case['host'].registry, executor_delta=1)
            outcomes.append('COMPLETED')
    assert outcomes == ['REVOKED', 'COMPLETED']


def test_u2_r03_uncertain_renamed_intent_is_closed():
    case = u2_setup(initial_effect=True, uncertain=True, task_id='task:u2:uncertain')
    initial = u2_advance(case)
    uncertain = initial.results[-1]
    assert uncertain.status == 'UNCERTAIN_CLOSED'
    original = case['host'].registry.action_packet_lifecycle_entries[0].root_bound_genesis
    calls = mocks.observed_mock_calls_v01()
    context = u2_context(case)
    trigger = work.build_work_revision_trigger_v01(context, work_id='original_read', output_field='content_ref')
    admitted = case['common']['catalogue'][2]
    renamed = work.WorkItemV01('coherent_renamed_effect', admitted.definition.definition_id, case['host'].owning_root_id,
        (work.WorkInputBindingV01('content_ref', trigger.output), runner.work_literal_v01('device_ref', 'REFERENCE', case['device'])),
        (case['device'],), (), None, None)
    revised, _ = u2_revise(case, initial, trigger=trigger, items=(renamed,))
    assert revised.program.candidate.revision_id != initial.program.candidate.revision_id
    successor = runner.authorize_action_v01(runner.build_native_from_business_v01(original.canonical_projection,
        admitted, uncertain.invocation.inputs, predecessor_packet_id=original.packet_identity.packet_id))
    assert successor.packet_identity.packet_id != original.packet_identity.packet_id
    assert successor.canonical_projection.idempotency_identity == original.canonical_projection.idempotency_identity
    with pytest.raises(ValueError, match='^uncertain_key_permanently_closed$') as semantic:
        action.record_action_packet_genesis_v01(case['host'].registry, root_bound_genesis=successor,
            action_packet_transition_registry_profile=transition.build_action_packet_transition_registry_profile_v01())
    with pytest.raises(ValueError, match='^host_duplicate_packet_binding$') as handler:
        u2_advance(case, revised)
    assert mocks.observed_mock_calls_v01() == calls and len(case['host'].work_attempts) == 2
    assert work.inspect_work_task_history_v01(u2_context(case))[0][1] == initial.results
    u2_emit('R03_UNCERTAIN_RENAMED', initial=initial, trigger=trigger, revised=revised, successor=successor,
        public_logical_key_reason=str(semantic.value), handler_no_second_install_reason=str(handler.value),
        attempts=case['host'].work_attempts, executor_delta=0)


def test_u2_r02_actual_recursive_review_child_accounting():
    import time
    start = time.monotonic()
    print('U2_D_STAGE=BUILD_CURRENT_SOURCE', flush=True)
    case = u2_setup(task_id='task:u2:children', with_review=True)
    print('U2_D_STAGE=SOURCE_BUILT elapsed=' + str(time.monotonic() - start), flush=True)
    with pytest.raises(ValueError, match='^work_task_review_not_observed$'):
        u2_advance(case)
    before = u2_context(case).snapshot
    print('U2_D_STAGE=PUBLIC_EXECUTION_AND_SUPPLIED_VALIDATION', flush=True)
    receipt = work.execute_work_task_review_v01(u2_context(case), obligation=case['obligation'],
        source_context=case['review_source'], semantic_proposal=case['common']['semantic_proposal'])
    assert type(receipt) is tuple and len(receipt) == 3
    obligation, source, bundle = receipt
    children = len(bundle.cell_results) - 1
    assert children > 0 and bundle.source_context == source
    assert work.validate_work_review_binding_v01(obligation, candidate=case['program'].candidate,
        item=case['program'].candidate.items[0], source_context=source, execution_bundle=bundle,
        semantic_proposal=case['common']['semantic_proposal']) == (True, ())
    after = u2_context(case).snapshot
    assert after.usage.children == children and after.usage.reserved_children == 0 and before.usage.children == 0
    assert [e[0] for e in case['host'].events] == ['TASK_D_REVIEW_RESERVED', 'TASK_D_REVIEW_COMPLETED']
    assert case['host'].events[0][-1] == source.runtime_policy.max_total_cells - 1
    reread = work.execute_work_task_review_v01(u2_context(case), obligation=obligation, source_context=source,
        semantic_proposal=case['common']['semantic_proposal'])
    assert reread is receipt and u2_context(case).snapshot == after
    initial = u2_advance(case, review_bindings=(receipt,))
    context = u2_context(case)
    trigger = work.build_work_revision_trigger_v01(context, work_id=initial.results[0].work_id, output_field='content_ref')
    items = u2_controlled_proposal(trigger, case['common']['catalogue'], case['host'].owning_root_id, case['device'], 1)
    with pytest.raises(ValueError, match='^work_task_remaining_budget$'):
        u2_revise(case, initial, trigger=trigger, items=items, budget=work.WorkBudgetV01(8, before.policy.max_children, 0, 7, 1))
    revised, _ = u2_revise(case, initial, trigger=trigger, items=items)
    assert revised.snapshot.usage.children == children and revised.program.candidate.budget.max_children == before.policy.max_children - children
    output = u2_advance(case, revised)
    assert output.status == 'COMPLETED' and output.snapshot.usage.children == children
    current = u2_context(case)
    next_trigger = work.build_work_revision_trigger_v01(current, work_id=output.results[-1].work_id, output_field='content_ref')
    reviewed_item = work.WorkItemV01('fresh_reviewed_property', case['common']['catalogue'][0].definition.definition_id,
        case['host'].owning_root_id, (work.WorkInputBindingV01('property', next_trigger.output),), (), (), None, 'review:pending_source')
    remaining = work.WorkBudgetV01(8, 24 - children, 0, 8 - current.snapshot.usage.compute_units, 0)
    with pytest.raises(ValueError, match='^work_task_required_review_removed$'):
        u2_revise(case, output, trigger=next_trigger, items=(replace(reviewed_item, review_obligation_id=None),), budget=remaining)
    preview = work.build_work_program_candidate_v01(task_id=output.program.candidate.task_id,
        previous_revision_id=output.program.candidate.revision_id, intent_ref=output.program.candidate.intent_ref,
        bsep_ref=output.program.candidate.bsep_ref, semantic_proposal_ref=output.program.candidate.semantic_proposal_ref,
        catalogue_revision=0, budget=remaining, items=(reviewed_item,), trigger_evidence_refs=(next_trigger.trigger_id,),
        continuation_context=replace(current, trigger=next_trigger), **case['common'])
    preview_program = work.materialize_work_program_v01(preview, continuation_context=replace(current, trigger=next_trigger), **case['common'])
    print('U2_D_STAGE=BUILD_CHANGED_CURRENT_SOURCE', flush=True)
    new_source, new_common = build_exact_review_source(preview_program, case['common'])
    new_obligation = work.build_work_review_obligation_v01(candidate=preview, item=reviewed_item, source_context=new_source)
    reviewed_item = replace(reviewed_item, review_obligation_id=new_obligation.obligation_id)
    accepted = work.revise_work_program_v01(current, previous_revision_id=output.program.candidate.revision_id,
        trigger=next_trigger, items=(reviewed_item,), budget=remaining, **new_common)
    case['common'] = new_common
    new_obligation = work.build_work_review_obligation_v01(candidate=accepted.program.candidate, item=reviewed_item, source_context=new_source)
    assert work.validate_work_review_binding_v01(new_obligation, candidate=accepted.program.candidate, item=reviewed_item,
        source_context=new_source, execution_bundle=bundle, semantic_proposal=new_common['semantic_proposal']) == (False, ('work_review_bundle_source',))
    with pytest.raises(ValueError, match='^work_task_review_not_observed$'):
        u2_advance(case, accepted, review_bindings=(receipt,))
    before_second = case['host'].work_attempts
    print('U2_D_STAGE=EXECUTE_CHANGED_SOURCE_REVIEW', flush=True)
    second_receipt = work.execute_work_task_review_v01(u2_context(case), obligation=new_obligation,
        source_context=new_source, semantic_proposal=new_common['semantic_proposal'])
    assert type(second_receipt) is tuple and second_receipt[2] is not bundle
    assert case['host'].work_attempts == before_second
    final = u2_advance(case, accepted, review_bindings=(second_receipt,))
    assert final.status == 'COMPLETED' and final.results[0].invocation.inputs[0].value == next_trigger.output.value.value
    assert final.snapshot.usage.children == children + len(second_receipt[2].cell_results) - 1
    final_snapshot = u2_context(case).snapshot
    assert work.inspect_work_task_review_v01(u2_context(case), obligation_id=obligation.obligation_id) is receipt
    assert u2_context(case).snapshot == final_snapshot
    print('U2_D_STAGE=ACCOUNTING_COMPLETE elapsed=' + str(time.monotonic() - start), flush=True)
    u2_emit('R02_ACTUAL_CHILDREN', source=source, bundle=bundle, obligation=obligation, initial=initial, revised=revised,
        completed=output, events=case['host'].events, child_units=children, model_calls=0,
        convention='len(actual_validated_bundle.cell_results)-1', trusted_boundary='fixed_public_D_producer_inside_host_lock')
    u2_emit('R02_CHANGED_WORK_REVIEW', next_trigger=next_trigger, accepted=accepted, source=new_source,
        obligation=new_obligation, bundle=second_receipt[2], completed=final, events=case['host'].events,
        old_review_rejection='work_review_bundle_source', old_history_read_additional_children=0)


def test_u2_r01_actual_foreign_trigger_and_direct_entry_refusals():
    left, right = u2_setup(task_id='task:u2:left'), u2_setup(task_id='task:u2:right')
    left_result, right_result = u2_advance(left), u2_advance(right)
    left_context, right_context = u2_context(left), u2_context(right)
    left_trigger = work.build_work_revision_trigger_v01(left_context, work_id='original_read', output_field='content_ref')
    right_trigger = work.build_work_revision_trigger_v01(right_context, work_id='original_read', output_field='content_ref')
    assert work.validate_work_revision_trigger_v01(left_trigger, context=left_context) == (True, ())
    assert work.validate_work_revision_trigger_v01(right_trigger, context=right_context) == (True, ())
    assert work.validate_work_revision_trigger_v01(right_trigger, context=left_context) == (False, ('work_task_trigger_predecessor',))
    assert work.validate_work_historical_output_v01(right_trigger.output, context=left_context) == (False, ('work_historical_foreign_task',))
    assert work.validate_work_task_snapshot_v01(left_context.snapshot, host=left['host']) == (True, ())
    inflated = replace(left_context.snapshot, policy=replace(left_context.snapshot.policy, max_compute_units=4096))
    assert work.validate_work_task_snapshot_v01(inflated, host=left['host']) == (False, ('work_task_stale_snapshot',))
    before = left['host'].events, left['host'].work_attempts, left_context.snapshot
    with pytest.raises(ValueError, match='^work_task_trigger_predecessor$'):
        u2_revise(left, left_result, trigger=right_trigger)
    admitted = left['common']['catalogue'][0]
    inputs = left_result.results[0].invocation.inputs
    with pytest.raises(ValueError, match='^work_task_dispatch_context_required$'):
        hosts.execute_admitted_pure_work_v01(left['host'], admission_id=admitted.admission_id,
            task_id=left_result.program.candidate.task_id, work_instance_id='work:coherent_renamed_unenrolled',
            inputs=inputs, expected_revision=left['host'].state_revision)
    with pytest.raises(ValueError, match='^work_task_enrollment_policy$'):
        work.enroll_work_program_v01(left['host'], left['program'], **left['common'], expected_revision=left['host'].state_revision)
    assert (left['host'].events, left['host'].work_attempts, u2_context(left).snapshot) == before
    accepted, _ = u2_revise(left, left_result, trigger=replace(left_trigger, output=replace(left_trigger.output)))
    assert accepted.status == 'ACTIVE'
    assert work.validate_work_revision_trigger_v01(left_trigger, context=u2_context(left)) == (False, ('work_task_trigger_predecessor',))
    u2_emit('R01_FOREIGN_ACTUAL_TRIGGER', left=left_result, right=right_result, left_trigger=left_trigger,
        right_trigger=right_trigger, accepted_equivalent=accepted, forbidden_start_delta=0)


def test_u2_r02_narrowed_budget_and_exact_serialized_controls():
    case = u2_setup()
    initial = u2_advance(case)
    trigger = work.build_work_revision_trigger_v01(u2_context(case), work_id='original_read', output_field='content_ref')
    proposal = u2_controlled_proposal(trigger, case['common']['catalogue'], case['host'].owning_root_id, case['device'], 1)
    narrowed = work.WorkBudgetV01(4, 3, 0, 3, 1)
    first, _ = u2_revise(case, initial, trigger=trigger, items=proposal, budget=narrowed)
    first = u2_advance(case, first)
    trigger2 = work.build_work_revision_trigger_v01(u2_context(case), work_id=first.results[-1].work_id, output_field='content_ref')
    one = work.WorkItemV01('last_bounded_transform', case['common']['catalogue'][1].definition.definition_id,
        case['host'].owning_root_id, (work.WorkInputBindingV01('content_ref', trigger2.output),), (), (), None, None)
    for name, budget in (('compute', work.WorkBudgetV01(4, 3, 0, 2, 0)), ('children', work.WorkBudgetV01(4, 4, 0, 1, 0)),
        ('items', work.WorkBudgetV01(5, 3, 0, 1, 0))):
        with pytest.raises(ValueError, match='^work_task_narrowed_budget$'):
            u2_revise(case, first, trigger=trigger2, items=(one,), budget=budget)
        u2_emit('R02_NARROWED.' + name, rejected_budget=budget, actual_state=u2_context(case).snapshot)
    second, _ = u2_revise(case, first, trigger=trigger2, items=(one,), budget=work.WorkBudgetV01(4, 3, 0, 1, 0))
    completed = u2_advance(case, second)
    assert completed.status == 'COMPLETED' and completed.snapshot.usage.compute_units == 4
    schema = json.loads((Path(work.__file__).resolve().parents[2] / 'schemas/work_composition_v01.schema.json').read_text())
    for kind, body in (('task_policy', actual_evidence_plain_v03(completed.snapshot.policy)),
        ('task_snapshot', actual_evidence_plain_v03(completed.snapshot)),
        ('historical_output', actual_evidence_plain_v03(trigger2.output)), ('revision_trigger', actual_evidence_plain_v03(trigger2))):
        validator = jsonschema.Draft202012Validator(dict(schema, **{'$ref': '#/$defs/' + kind}))
        validator.validate(body)
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(dict(body, authority_created=True))
    assert work.validate_work_continuation_outcome_v01(replace(completed, reason='caller_verdict'),
        context=u2_context(case), **case['common']) == (False, ('work_task_outcome_binding',))
    u2_emit('R02_NARROWED_EQUIVALENT', completed=completed)


def test_u2_r02_narrowed_child_reservation_refuses_before_start():
    import sys
    case = u2_setup(task_id='task:u2:narrowed_review_reproducer')
    initial = u2_advance(case)
    context = u2_context(case)
    trigger = work.build_work_revision_trigger_v01(context, work_id='original_read', output_field='content_ref')
    item = work.WorkItemV01('new_reviewed_read', case['common']['catalogue'][0].definition.definition_id,
        case['host'].owning_root_id, (work.WorkInputBindingV01('property', trigger.output),), (), (), None, 'review:pending')
    budget = work.WorkBudgetV01(8, 1, 0, 7, 1)
    preview = work.build_work_program_candidate_v01(task_id=initial.program.candidate.task_id,
        previous_revision_id=initial.program.candidate.revision_id, intent_ref=initial.program.candidate.intent_ref,
        bsep_ref=initial.program.candidate.bsep_ref, semantic_proposal_ref=initial.program.candidate.semantic_proposal_ref,
        catalogue_revision=0, budget=budget, items=(item,), trigger_evidence_refs=(trigger.trigger_id,),
        continuation_context=replace(context, trigger=trigger), **case['common'])
    materialized = work.materialize_work_program_v01(preview, continuation_context=replace(context, trigger=trigger), **case['common'])
    source, common = build_exact_review_source(materialized, case['common'])
    obligation = work.build_work_review_obligation_v01(candidate=preview, item=item, source_context=source)
    item = replace(item, review_obligation_id=obligation.obligation_id)
    accepted = work.revise_work_program_v01(context, previous_revision_id=initial.program.candidate.revision_id,
        trigger=trigger, items=(item,), budget=budget, **common)
    case['common'] = common
    obligation = work.build_work_review_obligation_v01(candidate=accepted.program.candidate, item=item, source_context=source)
    before = u2_context(case).snapshot
    calls = mocks.observed_mock_calls_v01()
    observed = []
    target_code = g2d.run_fractal_runtime_v02.__code__

    def observe(frame, event, arg):
        if event == 'call' and frame.f_code is target_code:
            observed.append('PUBLIC_D_CALL')

    prior_profiler = sys.getprofile()
    try:
        sys.setprofile(observe)
        result = work.execute_work_task_review_v01(u2_context(case), obligation=obligation,
            source_context=source, semantic_proposal=common['semantic_proposal'])
    finally:
        sys.setprofile(prior_profiler)
    assert source.runtime_policy.max_total_cells - 1 > budget.max_children
    assert before.policy.max_children == 24 and accepted.program.candidate.budget.max_children == 1
    assert result.status == 'EXHAUSTED' and result.reason == 'work_task_children_exhausted'
    assert result.snapshot.usage == before.usage and observed == []
    assert mocks.observed_mock_calls_v01() == calls
    assert not any(e[0] == 'TASK_D_REVIEW_RESERVED' for e in case['host'].events)
    assert work.validate_work_continuation_outcome_v01(result, context=u2_context(case), **common) == (True, ())
    after = u2_context(case).snapshot
    assert work.execute_work_task_review_v01(u2_context(case), obligation=obligation,
        source_context=source, semantic_proposal=common['semantic_proposal']) == result
    assert u2_context(case).snapshot == after and mocks.observed_mock_calls_v01() == calls
    u2_emit('R02_NARROWED_REVIEW_PRESTART', accepted=accepted, trigger=trigger, source=source, obligation=obligation,
        before=before, result=result, events=case['host'].events, observed_public_D_calls=len(observed),
        observation_scope='Read-only code-identity call observer around the actual public review entry; restored in finally.')
