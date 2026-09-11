"""Native/common first-slice proofs, not whole universality acceptance."""
from dataclasses import replace, fields, is_dataclass
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from hedgehog import action_commit_packet_v02 as action
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import transition_registry_v01 as transitions
from hedgehog import work_execution_host_v01 as hosts
from demo import run_action_packet_portability_v01 as runner
from demo import work_composition_mock_capabilities_v01 as mocks


def emit(case, **observed):
    print('CASE_RESULT=' + json.dumps(dict(case_id=case, **observed), sort_keys=True))


def execute_playback_equivalent_v02(invocation):
    return mocks.execute_playback_v01(invocation)


def public_transition_for(registry, bound, rule_id, now, *, materials=None, decision_id=None):
    profile = transitions.build_action_packet_transition_registry_profile_v01()
    rule = transitions.lookup_action_packet_transition_rule_v01(registry=profile, transition_rule_id=rule_id)
    c = bound.canonical_projection;packet = bound.packet_identity.packet_id
    root_id = bound.root_decision_projection.root_decision_result.decision_id
    entry = next(e for e in registry.action_packet_lifecycle_entries if e.root_bound_genesis.packet_identity.packet_id == packet)
    bindings = []
    for code in rule.required_evidence_codes:
        material = materials[code] if materials is not None else ('evidence:u1:' + code,
            action.domain_separated_sha256_hex_v01(domain='demo.u1.transition_evidence.v01',
                payload=action.canonical_material_bytes_v01((('packet_id', packet), ('root_decision_id', root_id), ('evidence_code', code)))),
            'validator:u1:public_lifecycle')
        bindings.append(action.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id, evidence_code=code, evidence_ref=material[0], evidence_sha256=material[1], validator_profile_id=material[2]))
    attempt = action.build_action_execution_attempt_identity_v01(packet_id=packet,
        idempotency_key=c.idempotency_identity.idempotency_key, attempt_ordinal=1,
        evaluation_context_id='context:u1:dispatch') if rule_id == 'g2a_t03_pending' else None
    return action.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,
        transition_rule_id=rule_id, packet_id=packet, idempotency_key=c.idempotency_identity.idempotency_key,
        previous_transition_event_id=entry.transition_events[-1].transition_event_id if entry.transition_events else None,
        owning_local_root_id=c.owning_local_root_id, root_decision_ref=(decision_id if decision_id is not None else
            root_id if rule_id == 'g2a_t01_activate_root_authorization' else None), transition_evidence_bindings=tuple(bindings),
        dependency_set_candidate_fingerprint=c.dependency_set_candidate_fingerprint, temporal_authority_fingerprint=c.temporal_authority_fingerprint,
        evaluation_time=now, evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:dispatch',
        execution_attempt_identity=attempt, receipt_ref=None)


def native_corridor_for(bound):
    c = bound.canonical_projection;packet = bound.packet_identity.packet_id
    step = action.build_common_corridor_step_v01(transaction_id=c.transaction_id, owning_local_root_id=c.owning_local_root_id,
        packet_id=packet, authorization_candidate_id=c.authorization_candidate.root_packet_authorization_candidate_id,
        action_class=c.selected_canonical_action, adapter_binding=c.adapter_binding, subject_scope=c.normalized_subject_scope,
        target_scope=c.normalized_target_scope, effect_parameters=c.normalized_effect_parameters,
        issued_at_utc=c.temporal_authority.issued_at_utc, expires_at_utc=c.temporal_authority.expires_at_utc)
    corridor = action.build_common_contract_fulfillment_corridor_v01(transaction_id=c.transaction_id,
        owning_local_root_id=c.owning_local_root_id, packet_id=packet, corridor_class=c.adapter_binding.corridor_class, steps=(step,))
    return corridor, step


def host_with_independent_and_successor(p, include_successor=True):
    independent = runner.prepare_native_playback_v01(content_ref='content:u1:independent')
    c, admitted, inputs = runner.build_native_playback_candidate_v01()
    successor = runner.authorize_action_v01(runner.build_native_from_business_v01(c, admitted, inputs,
        predecessor_packet_id=p.root_bound.packet_identity.packet_id))
    profile = transitions.build_action_packet_transition_registry_profile_v01()
    registry = action.record_action_packet_genesis_v01(p.registry, root_bound_genesis=independent.root_bound,
        action_packet_transition_registry_profile=profile)
    entry = independent.registry.action_packet_lifecycle_entries[0]
    iid = independent.root_bound.packet_identity.packet_id
    registry = action.activate_action_packet_lifecycle_v01(registry, packet_id=iid,
        transition_event=entry.transition_events[0], disposition_event=independent.registry.idempotency_disposition_events[0],
        action_packet_transition_registry_profile=profile)
    for event in entry.transition_events[1:]:
        registry = action.append_action_packet_lifecycle_transition_v01(registry, packet_id=iid,
            transition_event=event, action_packet_transition_registry_profile=profile)
    if include_successor:
        registry = action.record_action_packet_genesis_v01(registry, root_bound_genesis=successor,
            action_packet_transition_registry_profile=profile)
    corridor, step = native_corridor_for(successor)
    bindings = tuple((v.root_bound.packet_identity.packet_id, v.corridor, v.corridor_step, v.admitted.admission_id, v.inputs)
        for v in (p, independent))
    if include_successor:
        bindings += ((successor.packet_identity.packet_id, corridor, step, admitted.admission_id, inputs),)
    catalogue = {}
    for value in (p.admitted, independent.admitted) + ((admitted,) if include_successor else ()):
        if value.admission_id in catalogue:
            assert firewall.snapshot_admitted_capability_v01(value) == firewall.snapshot_admitted_capability_v01(catalogue[value.admission_id])
        else:
            catalogue[value.admission_id] = value
    host = hosts.build_root_work_execution_host_v01(owning_root_id=c.owning_local_root_id, registry=registry,
        catalogue=tuple(catalogue.values()), packet_bindings=bindings,
        current_dependency_observations=p.observations, logical_time_bridge=p.bridge,
        trusted_source=mocks.TrustedMockWorkSourceV01(p.observations, p.bridge, 1014, 'u1.controlled_utc', 'context:u1:dispatch'))
    return host, independent, successor if include_successor else None


def test_s03_mixed_encoding_outstanding_reservation_transfers_under_real_root():
    old = runner.authorize_and_prepare_action_v01(runner.build_legacy_payment_candidate_v01())
    predecessor = old.root_bound;pc = predecessor.canonical_projection;pid = predecessor.packet_identity.packet_id
    canonical, admitted, inputs = runner.build_native_payment_candidate_v01(predecessor_packet_id=pid)
    successor = runner.authorize_action_v01(canonical);sid = successor.packet_identity.packet_id
    assert canonical.idempotency_identity == pc.idempotency_identity
    profile = transitions.build_action_packet_transition_registry_profile_v01()
    registry = action.record_action_packet_genesis_v01(old.registry, root_bound_genesis=successor,
        action_packet_transition_registry_profile=profile)
    candidate = action.build_supersession_candidate_v01(owning_local_root_id=pc.owning_local_root_id,
        predecessor_packet_id=pid, successor_packet_authorization_candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,
        stable_logical_intent_id=canonical.logical_intent.root_owned_intent_id, idempotency_key=canonical.idempotency_identity.idempotency_key,
        supersession_reason_class=canonical.authorization_candidate.supersession_reason_class, policy_fingerprint=pc.authority_policy_fingerprint)
    kernel, decision_input, result = runner.review_native_candidate_v01(canonical, 'mixed_supersession',
        candidate_kind='SUPERSESSION', candidate_id=candidate.supersession_candidate_id, predecessor=predecessor)
    root = action.build_root_decision_candidate_projection_v01(candidate_kind='SUPERSESSION',
        projected_candidate_id=candidate.supersession_candidate_id, root_decision_kernel=kernel,
        root_decision_input=decision_input, root_decision_result=result)
    accepted = action.build_accepted_supersession_binding_v01(candidate=candidate, root_projection=root,
        predecessor=predecessor, successor=successor)
    now = canonical.evaluation_time + 4;dep = pc.dependency_candidate.dependency_records[0]
    invalidation = action.build_action_invalidation_evidence_v01(source_invalidation_event_ref='source:u1:root_supersession',
        packet_id=pid, dependency_id='dependency:u1:root_supersession', invalidation_class='ROOT_SUPERSESSION',
        evidence_ref=accepted.accepted_supersession_binding_id, evidence_sha256=accepted.accepted_supersession_binding_id.split(':', 1)[1],
        observed_status='OBSERVED_ROOT_SUPERSESSION', time_envelope_id=dep.time_envelope_id, freshness_policy_id=dep.freshness_policy_id,
        owning_local_root_id=pc.owning_local_root_id, accepted_by_local_root_id=pc.owning_local_root_id,
        acceptance_root_decision_id=accepted.supersession_root_decision_id, acceptance_root_decision_hash=accepted.supersession_root_decision_hash,
        authority_effect='ROOT_SUPERSESSION', root_decision_ref=accepted.supersession_root_decision_id,
        evaluation_time=now, evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:dispatch')
    state = action.derive_action_packet_lifecycle_state_v01(registry, packet_id=pid)
    latest = old.registry.action_packet_lifecycle_entries[0].transition_events[-1]
    materials = {
        'successor_packet_valid': (sid, sid.split(':', 1)[1], 'action_commit_packet_identity_profile_v01'),
        'accepted_supersession_binding_valid': (accepted.accepted_supersession_binding_id,
            accepted.accepted_supersession_binding_id.split(':', 1)[1], 'accepted_supersession_binding_v01'),
        'predecessor_binding_valid': (pid, pid.split(':', 1)[1], 'action_commit_packet_identity_profile_v01'),
        'idempotency_transfer_valid': (state.latest_disposition_event_id, state.latest_disposition_event_id.split(':', 1)[1],
            action.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01),
        'adapter_not_called': (latest.execution_attempt_id, latest.execution_attempt_id.split(':', 1)[1], action.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01),
    }
    supersede = public_transition_for(registry, predecessor, 'g2a_t22_pending_supersede', now,
        materials=materials, decision_id=result.decision_id)
    activate = public_transition_for(registry, successor, 'g2a_t01_activate_root_authorization', now)
    transfer = action.build_idempotency_disposition_event_v01(idempotency_key=canonical.idempotency_identity.idempotency_key,
        event_class='TRANSFER_SUPERSESSION', from_disposition='RESERVED', to_disposition='RESERVED', from_owner_packet_id=pid,
        to_owner_packet_id=sid, previous_disposition_event_id=state.latest_disposition_event_id,
        cause_transition_event_ids=(supersede.transition_event_id, activate.transition_event_id),
        root_decision_ref=successor.root_decision_projection.root_decision_result.decision_id, predecessor_packet_id=pid, successor_packet_id=sid,
        evidence_refs=tuple(sorted((accepted.accepted_supersession_binding_id, pc.logical_intent.root_owned_intent_id,
            successor.root_decision_projection.root_decision_result.decision_id))), evaluation_time=now,
        evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:dispatch')
    registry = action.record_action_packet_supersession_v01(registry, predecessor_packet_id=pid, successor_packet_id=sid,
        supersession_candidate=candidate, supersession_root_projection=root, accepted_supersession_binding=accepted,
        invalidation_evidence=invalidation, successor_activation_event=activate, disposition_event=transfer,
        action_packet_transition_registry_profile=profile, predecessor_supersession_event=supersede)
    assert action.derive_action_packet_lifecycle_state_v01(registry, packet_id=pid).lifecycle_state == 'SUPERSEDED'
    new_state = action.derive_action_packet_lifecycle_state_v01(registry, packet_id=sid)
    assert new_state.idempotency_disposition == 'RESERVED' and new_state.reservation_owner_packet_id == sid
    for rule in ('g2a_t02_queue', 'g2a_t03_pending'):
        event = public_transition_for(registry, successor, rule, now)
        registry = action.append_action_packet_lifecycle_transition_v01(registry, packet_id=sid,
            transition_event=event, action_packet_transition_registry_profile=profile)
    corridor, step = native_corridor_for(successor)
    host = hosts.build_root_work_execution_host_v01(owning_root_id=pc.owning_local_root_id, registry=registry,
        catalogue=(admitted,), packet_bindings=((pid, old.corridor, old.corridor_step, None, None),
            (sid, corridor, step, admitted.admission_id, inputs)), current_dependency_observations=old.observations,
        logical_time_bridge=old.bridge, trusted_source=mocks.TrustedMockWorkSourceV01(old.observations, old.bridge,
            now, 'u1.controlled_utc', 'context:u1:dispatch'))
    before = len(mocks.observed_mock_calls_v01())
    with pytest.raises(ValueError, match='^host_current_action_not_executable$'):
        host.dispatch(**dispatch_kwargs(old))
    consumed = host.dispatch(**dict(dispatch_kwargs(old), packet_id=sid))
    assert consumed.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    assert sum(c[0] == 'EXECUTOR_STARTED' for c in mocks.observed_mock_calls_v01()[before:]) == 1
    assert host.replay(packet_id=pid).reconstructed_state.lifecycle_state == 'SUPERSEDED'
    emit('S03.OUTSTANDING_TRANSFER', source_encoding='SUPPLIER_V02', successor_encoding='NATIVE_V01',
        transfer_class=transfer.event_class, actual_executor_starts=1, predecessor='SUPERSEDED', successor='CONSUMED')


_INTERRUPTED_STARTS = []


def execute_playback_interrupt_v01(invocation):
    _INTERRUPTED_STARTS.append(invocation.invocation_id)
    raise KeyboardInterrupt('controlled_actual_executor_start')


def validate_playback_refused_inputs_v01(definition, inputs):
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=False, reason_codes=('controlled_input_refusal',))


def test_n01_public_start_checks_actual_inputs_and_new_code_against_root(monkeypatch):
    for variant in ('beta_inputs', 'new_code'):
        p = runner.prepare_native_playback_v01()
        other = (runner.prepare_native_playback_v01(content_ref='content:u1:beta') if variant == 'beta_inputs'
            else variant_prepared(execute_playback_equivalent_v02))
        # Both inputs/code have their own real Root authorization and execution.
        fresh_admitted = hosts.admit_local_capability_v01(definition=other.admitted.definition,
            input_validator=other.admitted.input_validator, output_validator=other.admitted.output_validator,
            executor=other.admitted.executor, catalogue_revision=other.admitted.catalogue_revision,
            host_instance_ref=other.admitted.host_instance_ref)
        _, own = runner.dispatch_prepared_action_v01(replace(other, admitted=fresh_admitted))
        assert own.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
        actual = firewall.execute_bound_effect_v01
        observed = []
        def cross_feed(**values):
            old = values['invocation']
            invocation = firewall.build_bound_capability_invocation_v01(admitted_capability=other.admitted,
                task_id=old.task_id, work_instance_id=old.work_instance_id, owning_root_id=old.owning_root_id,
                candidate_id=other.root_bound.canonical_projection.authorization_candidate.root_packet_authorization_candidate_id,
                packet_id=old.packet_id, execution_attempt_id=old.execution_attempt_id, inputs=other.inputs,
                resource_refs=other.admitted.definition.resource_refs, canonical_projection=other.root_bound.canonical_projection)
            invocation = reidentify_native(replace(invocation, candidate_id=old.candidate_id),
                'capability_invocation', 'invocation_id')
            assert not firewall.validate_bound_capability_invocation_v01(invocation,
                firewall.snapshot_admitted_capability_v01(other.admitted))
            before = mocks.observed_mock_calls_v01()
            reason = 'capability_business_input_binding:content_ref' if variant == 'beta_inputs' else 'capability_invocation_candidate_binding'
            with pytest.raises(ValueError, match='^' + reason + '$') as error:
                actual(**dict(values, invocation=invocation, admitted_capability=other.admitted))
            assert mocks.observed_mock_calls_v01() == before
            assert values['firewall']._state.started_capability_ids == set()
            observed.append(str(error.value))
            raise ValueError(str(error.value))
        with monkeypatch.context() as patch:
            patch.setattr(firewall, 'execute_bound_effect_v01', cross_feed)
            with pytest.raises(ValueError):
                runner.dispatch_prepared_action_v01(p)
        assert len(observed) == 1
        emit('N01.' + variant, positive='OWN_ROOT_CONSUMED', public_rejection=observed[0], executor_starts=0)


def subject_role_prepared(included):
    c, old, inputs = runner.build_native_playback_candidate_v01()
    d = old.definition
    semantics = d.business_semantics
    bindings = tuple(firewall.build_capability_business_input_binding_v01(input_name=b.input_name,
        source_kind='SUBJECT_RECORD' if b.input_name == 'content_ref' else b.source_kind,
        source_name=b.input_name if b.input_name == 'content_ref' else b.source_name, value_type=b.value_type)
        for b in semantics.input_bindings)
    semantics = firewall.build_capability_business_semantics_v01(**dict(
        {f.name: getattr(semantics, f.name) for f in fields(semantics)}, input_bindings=bindings))
    definition = firewall.build_capability_definition_v01(**dict({f.name: getattr(d, f.name) for f in fields(d)
        if f.name not in ('definition_id', 'contract_sha256')}, business_semantics=semantics))
    admitted = hosts.admit_local_capability_v01(definition=definition, input_validator=mocks.validate_playback_inputs_v01,
        output_validator=mocks.validate_playback_output_v01, executor=mocks.execute_playback_v01,
        catalogue_revision=0, host_instance_ref='host:u1:subject_scope')
    c = runner.build_native_from_business_v01(replace(c,
        normalized_subject_scope=action.build_action_subject_scope_profile_v01(
            included_subject_refs=('content:u1:alpha', 'content:u1:beta'), excluded_subject_refs=()),
        consequential_effect_parameters=action.build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=None, currency_code=None, quantity_decimal=None, parameter_records=inputs)), admitted, inputs)
    p = runner.authorize_and_prepare_action_v01(c, admitted, inputs)
    step = action.build_common_corridor_step_v01(**dict({f.name: getattr(p.corridor_step, f.name)
        for f in fields(p.corridor_step) if f.name != 'step_id'}, subject_scope=action.build_action_subject_scope_profile_v01(
            included_subject_refs=(included,), excluded_subject_refs=())))
    corridor = action.build_common_contract_fulfillment_corridor_v01(**dict({f.name: getattr(p.corridor, f.name)
        for f in fields(p.corridor) if f.name != 'corridor_id'}, steps=(step,)))
    return replace(p, corridor= corridor, corridor_step=step)


def test_n02_subject_role_is_consumed_inside_effective_narrowed_scope():
    for included in ('content:u1:alpha', 'content:u1:beta'):
        p = subject_role_prepared(included)
        before = len(mocks.observed_mock_calls_v01())
        host = runner.host_for_prepared_action_v01(p)
        if included == 'content:u1:alpha':
            out = host.dispatch(**dispatch_kwargs(p))
            assert out.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
            starts = 1
        else:
            with pytest.raises(ValueError, match='^native_dispatch_narrowed_subject$'):
                host.dispatch(**dispatch_kwargs(p))
            assert host.registry is p.registry and host.revision == 0 and host.unresolved_starts == ()
            starts = 0
        assert sum(c[0] == 'EXECUTOR_STARTED' for c in mocks.observed_mock_calls_v01()[before:]) == starts
        emit('N02.' + included, actual_executor_starts=starts, effective_subject=included,
            actual_subject='content:u1:alpha', target=p.corridor_step.target_scope.included_target_refs, time=1014)


def test_n03_started_interrupt_and_post_result_escape_remain_closed_in_same_host(monkeypatch):
    for fault in ('executor_interrupt', 'post_result_escape'):
        p = variant_prepared(execute_playback_interrupt_v01) if fault == 'executor_interrupt' else runner.prepare_native_playback_v01()
        host, independent, successor = host_with_independent_and_successor(p, fault == 'executor_interrupt')
        interrupt_before = len(_INTERRUPTED_STARTS)
        calls_before = len(mocks.observed_mock_calls_v01())
        actual = action.execute_action_packet_mock_fulfillment_v01
        def after_result(*args, **kwargs):
            genuine = actual(*args, **kwargs)
            assert action.validate_action_commit_packet_registry_v02(genuine)[0]
            raise KeyboardInterrupt('controlled_after_actual_result_before_host_install')
        with monkeypatch.context() as patch:
            if fault == 'post_result_escape':
                patch.setattr(action, 'execute_action_packet_mock_fulfillment_v01', after_result)
            with pytest.raises(KeyboardInterrupt):
                hosts.dispatch_current_action_v01(host, **dispatch_kwargs(p))
        assert host.revision == 1 and len(host.unresolved_starts) == 1
        key, invocation = host.unresolved_starts[0]
        assert key == p.root_bound.canonical_projection.idempotency_identity.idempotency_key
        assert invocation.packet_id == p.root_bound.packet_identity.packet_id
        with pytest.raises(ValueError, match='^host_common_key_inflight_closed$'):
            hosts.dispatch_current_action_v01(host, **dispatch_kwargs(p, host.revision))
        if successor is not None:
            assert successor.canonical_projection.idempotency_identity.idempotency_key == key
            with pytest.raises(ValueError, match='^host_common_key_inflight_closed$'):
                hosts.dispatch_current_action_v01(host, **dict(dispatch_kwargs(p, host.revision),
                    packet_id=successor.packet_identity.packet_id))
        starts = (len(_INTERRUPTED_STARTS) - interrupt_before if fault == 'executor_interrupt' else
            sum(c[0] == 'EXECUTOR_STARTED' for c in mocks.observed_mock_calls_v01()[calls_before:]))
        assert starts == 1
        own = host.dispatch(**dispatch_kwargs(independent, host.revision))
        assert own.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
        assert host.revision == 2 and len(host.unresolved_starts) == 1
        emit('N03.' + fault, same_host_current_revision=host.revision, executor_starts=starts,
            retained_common_key=key, retry='host_common_key_inflight_closed',
            code_successor='host_common_key_inflight_closed' if successor is not None else 'COVERED_BY_EXECUTOR_INTERRUPT_CASE',
            same_host_unrelated='CONSUMED')


def test_independent_reserved_keys_execute_in_either_order_with_exact_history():
    for reverse in (False, True):
        p = runner.prepare_native_playback_v01()
        host, independent, _ = host_with_independent_and_successor(p, False)
        for item in ((independent, p) if reverse else (p, independent)):
            result = host.dispatch(**dispatch_kwargs(item, host.revision))
            assert action.validate_action_commit_packet_registry_v02(result)[0]
            assert result.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
        assert host.revision == 2 and host.unresolved_starts == ()
        assert len(host.registry.action_packet_fulfillment_attempt_contexts) == 2
        emit('N03.independent_history.' + str(reverse), consumed=2, unresolved=0)


def test_n04_same_host_refreshes_trusted_dependency_and_rejects_old_task_time():
    p = runner.prepare_native_playback_v01()
    source = mocks.TrustedMockWorkSourceV01(p.observations, p.bridge, 1014, 'u1.controlled_utc', 'context:u1:dispatch')
    host = runner.host_for_prepared_action_v01(p, source)
    query = dispatch_kwargs(p);query.pop('task_id')
    assert hosts.inspect_current_action_v01(host, **query).present_executable
    old = p.observations[0]
    digest = action.domain_separated_sha256_hex_v01(domain='demo.u1.dependency.v01',
        payload=action.canonical_material_bytes_v01((('availability', 'CONTROLLED_UNAVAILABLE'),)))
    envelope = action.build_action_dependency_time_envelope_id_v01(dependency_id=old.dependency_id,
        evidence_ref=old.evidence_ref, content_sha256=digest, freshness_policy_id=old.freshness_policy_id,
        source_provenance_refs=old.source_provenance_refs, valid_from_utc=old.valid_from_utc, valid_to_utc=old.valid_to_utc)
    changed = action.build_action_dependency_current_observation_v01(dependency_id=old.dependency_id,
        evidence_ref=old.evidence_ref, observed_content_sha256=digest, time_envelope_id=envelope,
        freshness_policy_id=old.freshness_policy_id, source_provenance_refs=old.source_provenance_refs,
        valid_from_utc=old.valid_from_utc, valid_to_utc=old.valid_to_utc, observed_at_utc=1015,
        observation_context_id='context:u1:dispatch')
    source.advance_v01(evaluation_time=1015, observations=(changed,))
    inspection = hosts.inspect_current_action_v01(host, **dict(query, evaluation_time=1015))
    assert not inspection.present_executable and host.current_sources.observations == (changed,) and host.revision == 1
    before = mocks.observed_mock_calls_v01()
    with pytest.raises(ValueError, match='^host_current_action_not_executable$'):
        host.dispatch(**dict(dispatch_kwargs(p, host.revision), evaluation_time=1015))
    with pytest.raises(ValueError, match='^host_task_time_not_current$'):
        host.dispatch(**dispatch_kwargs(p, host.revision))
    assert mocks.observed_mock_calls_v01() == before and host.registry is p.registry and not host.unresolved_starts
    neighbor = runner.prepare_native_playback_v01()
    fresh = mocks.TrustedMockWorkSourceV01(neighbor.observations, neighbor.bridge, 1015, 'u1.controlled_utc', 'context:u1:dispatch')
    positive = runner.host_for_prepared_action_v01(neighbor, fresh).dispatch(**dict(dispatch_kwargs(neighbor), evaluation_time=1015))
    assert positive.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    emit('N04.TRUSTED_REFRESH', actual_dependency=digest, current_time=1015, source_revision=host.current_sources.source_revision,
        present_executable=inspection.present_executable, changed_source_refusal=True, old_task_time_refused=True, unchanged_neighbor='CONSUMED')


def test_n03_real_input_refusal_never_records_started_or_consumed():
    c, original, inputs = runner.build_native_playback_candidate_v01()
    d = original.definition
    source = hosts.observe_local_capability_code_v01(validate_playback_refused_inputs_v01)
    definition = firewall.build_capability_definition_v01(**dict({f.name: getattr(d, f.name) for f in fields(d)
        if f.name not in ('definition_id', 'contract_sha256')}, input_validator_ref=source.public_symbol,
        code_sha256s=tuple((source.public_symbol, source.source_sha256) if name == d.input_validator_ref else (name, sha)
            for name, sha in d.code_sha256s)))
    admitted = hosts.admit_local_capability_v01(definition=definition, input_validator=validate_playback_refused_inputs_v01,
        output_validator=original.output_validator, executor=original.executor, catalogue_revision=0,
        host_instance_ref='host:u1:input_refusal')
    p = runner.authorize_and_prepare_action_v01(runner.build_native_from_business_v01(c, admitted, inputs), admitted, inputs)
    host = runner.host_for_prepared_action_v01(p)
    before = mocks.observed_mock_calls_v01()
    with pytest.raises(ValueError, match='^capability_input_validation_failed:controlled_input_refusal$'):
        host.dispatch(**dispatch_kwargs(p))
    assert host.registry is p.registry and host.revision == 0 and host.events == () and host.unresolved_starts == ()
    assert mocks.observed_mock_calls_v01() == before
    assert action.derive_action_packet_lifecycle_state_v01(host.registry,
        packet_id=p.root_bound.packet_identity.packet_id).idempotency_disposition == 'RESERVED'
    emit('N03.PRESTART_INPUT_REFUSAL', actual_reason='controlled_input_refusal', executor_starts=0,
        disposition='RESERVED', host_revision=0)


def test_n05_per_instance_catalogue_cannot_be_cross_fed_and_replay_is_retained(monkeypatch):
    p = runner.prepare_native_playback_v01()
    owner = runner.host_for_prepared_action_v01(p)
    with pytest.raises(ValueError, match='^host_foreign_catalogue_origin$'):
        runner.host_for_prepared_action_v01(p)
    assert owner.revision == 0 and owner.registry is p.registry
    for changed in (replace(p.admitted), replace(p.admitted, executor=mocks.execute_playback_wrong_output_v01),
        replace(p.admitted, output_validator=mocks.validate_payment_output_v01), replace(p.admitted, _origin=None)):
        assert firewall.validate_admitted_capability_v01(changed) == ('capability_not_trusted_admission',)
    genuine = mocks.admit_playback_v01('device:u1:one', 'host:u1:playback')
    assert genuine is not p.admitted and firewall.snapshot_admitted_capability_v01(genuine) == firewall.snapshot_admitted_capability_v01(p.admitted)
    _, result = runner.dispatch_prepared_action_v01(replace(p, admitted=genuine))
    before = mocks.observed_mock_calls_v01()
    def unexpected_io(*args, **kwargs):
        raise AssertionError('historical_replay_touched_live_source')
    with monkeypatch.context() as patch:
        patch.setattr(Path, 'read_bytes', unexpected_io)
        patch.setattr(hosts, 'observe_local_capability_code_v01', unexpected_io)
        replay = action.replay_action_packet_lifecycle_history_v01(result, packet_id=p.root_bound.packet_identity.packet_id)
        assert firewall.validate_admitted_capability_v01(genuine) == ()
    assert replay.reconstructed_state.idempotency_disposition == 'CONSUMED' and mocks.observed_mock_calls_v01() == before
    emit('N05.ORIGIN_AND_REPLAY', foreign_host_refused=True, genuine_equivalent='CONSUMED',
        replay_filesystem_or_live_observer_calls=0, replay_business_calls=0, in_memory_admission_validation=True)


def test_n05_trusted_refresh_detects_source_and_loaded_code_changes(tmp_path):
    import importlib.util
    source = tmp_path / 'explicit_capability_fixture.py'
    body = ('from demo import work_composition_mock_capabilities_v01 as mocks\n'
        'def execute_fixture_v01(invocation):\n    return mocks.execute_playback_v01(invocation)\n'
        'def execute_changed_v01(invocation):\n    raise RuntimeError("not_the_admitted_code")\n')
    source.write_text(body, encoding='utf-8')
    spec = importlib.util.spec_from_file_location('explicit_u1_capability_fixture', source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        p = variant_prepared(module.execute_fixture_v01)
        host = runner.host_for_prepared_action_v01(p)
        calls = mocks.observed_mock_calls_v01()
        original_code = module.execute_fixture_v01.__code__
        module.execute_fixture_v01.__code__ = module.execute_changed_v01.__code__
        with pytest.raises(ValueError, match='^capability_loaded_code_changed$'):
            host.dispatch(**dispatch_kwargs(p))
        module.execute_fixture_v01.__code__ = original_code
        # A real trusted file change, not a modified protected project module.
        source.write_text(body + '# trusted source revision\n', encoding='utf-8')
        with pytest.raises(ValueError, match='^capability_current_code_changed$'):
            host.dispatch(**dispatch_kwargs(p))
        assert mocks.observed_mock_calls_v01() == calls and host.revision == 0 and host.unresolved_starts == ()
        fresh = variant_prepared(module.execute_fixture_v01)
        assert fresh.root_bound.canonical_projection.idempotency_identity == p.root_bound.canonical_projection.idempotency_identity
        assert fresh.root_bound.canonical_projection.authorization_candidate != p.root_bound.canonical_projection.authorization_candidate
        _, accepted = runner.dispatch_prepared_action_v01(fresh)
        assert accepted.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
        emit('N05.SOURCE_CODE', changed_loaded_code_refused=True, changed_source_refused=True,
            fresh_source_own_root='CONSUMED', shared_business_key=True, protected_files_changed=0)
    finally:
        sys.modules.pop(spec.name, None)


def dispatch_kwargs(prepared, revision=0):
    return dict(packet_id=prepared.root_bound.packet_identity.packet_id, task_id='task:u1:controlled_dispatch',
        expected_revision=revision, evaluation_time=prepared.root_bound.canonical_projection.evaluation_time+4,
        evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:dispatch')


def fresh_prepared_catalogue(p):
    old = p.admitted
    admitted = hosts.admit_local_capability_v01(definition=old.definition, input_validator=old.input_validator,
        output_validator=old.output_validator, executor=old.executor, catalogue_revision=old.catalogue_revision,
        host_instance_ref=old.host_instance_ref)
    assert admitted is not old and firewall.snapshot_admitted_capability_v01(admitted) == firewall.snapshot_admitted_capability_v01(old)
    return replace(p, admitted=admitted)


def typed_material(value):
    if value is None:
        return action.ABSENT_V01
    if type(value) in (str, int, bool):
        return value
    if type(value) is tuple:
        return tuple(typed_material(v) for v in value)
    if type(value) is action.ActionEffectParameterRecordV01:
        return action.action_effect_parameter_record_material_v01(value)
    assert is_dataclass(value)
    return tuple((f.name, typed_material(getattr(value, f.name))) for f in fields(value))


def reidentify_native(value, leaf, id_field):
    material = tuple((f.name, typed_material(getattr(value, f.name))) for f in fields(value) if f.name != id_field)
    return replace(value, **{id_field: action.build_domain_separated_identity_v01(
        domain='hedgehog.common_action.' + leaf + '.v01', prefix=leaf + ':', material=material)})


def plain_material(value):
    if value is None:
        return action.ABSENT_V01
    if type(value) in (str, int, bool):
        return value
    if type(value) is list:
        return tuple(plain_material(v) for v in value)
    assert type(value) is dict
    return tuple((k, plain_material(value[k])) for k in sorted(value))


def rebuilt_receipt(plain, *, native):
    """Refresh local identity only, never manufacture execution or validation."""
    plain = copy.deepcopy(plain)
    if native:
        material = (('payload', tuple((k, plain_material(plain['payload'][k]))
            for k in sorted(plain['payload']) if k != 'receipt_ref')),
            ('envelope', tuple((k, plain_material(plain[k])) for k in (
                'abi_version', 'artifact_type', 'schema_version', 'transaction_id', 'owner_root_id',
                'source_component', 'authority_class', 'lifecycle_state', 'trace_refs', 'parent_refs', 'time_envelope'))))
        identifier = action.build_domain_separated_identity_v01(domain='hedgehog.common_action.native_effect_receipt.v01',
            prefix='effect_receipt_v01:', material=material)
        plain['artifact_id'] = plain['payload']['receipt_ref'] = identifier
    return abi.build_kernel_artifact_v01(**dict(plain, trace_refs=tuple(plain['trace_refs']), parent_refs=tuple(plain['parent_refs'])))


def coherent_receipt_history(registry, receipt):
    """Rebuild affected content identities and consumer references, not authority."""
    context = registry.action_packet_fulfillment_attempt_contexts[-1]
    original = context.attempt_evidence
    receipt_hash = action.domain_separated_sha256_hex_v01(domain='HEDGEHOG_ACTION_PACKET_EFFECT_RECEIPT_HASH_V01',
        payload=action.canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(receipt)))
    kwargs = {f.name: getattr(original, f.name) for f in fields(original)
        if f.name not in ('attempt_evidence_id', 'evidence_profile_id')}
    evidence = action.build_action_packet_fulfillment_attempt_evidence_v01(**dict(kwargs,
        receipt_ref=receipt.artifact_id, receipt_sha256=receipt_hash))
    entry = registry.action_packet_lifecycle_entries[-1]
    old_event = entry.transition_events[-1]
    profile = transitions.build_action_packet_transition_registry_profile_v01()
    bindings = []
    for binding in old_event.transition_evidence_bindings:
        values = {name: getattr(binding, name) for name in
            ('evidence_code', 'evidence_ref', 'evidence_sha256', 'validator_profile_id')}
        if binding.evidence_ref == original.attempt_evidence_id:
            values.update(evidence_ref=evidence.attempt_evidence_id,
                evidence_sha256=evidence.attempt_evidence_id.removeprefix(action.ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01))
        elif binding.evidence_ref == context.receipt.artifact_id:
            values.update(evidence_ref=receipt.artifact_id, evidence_sha256=receipt_hash)
        bindings.append(action.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,
            transition_rule_id=old_event.transition_rule_id, **values))
    event = replace(old_event, receipt_ref=receipt.artifact_id if old_event.receipt_ref is not None else None,
        transition_evidence_bindings=tuple(bindings))
    event = replace(event, transition_event_id=action.build_domain_separated_identity_v01(
        domain=action.ACTION_PACKET_TRANSITION_EVENT_DOMAIN_V01, prefix=action.ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
        material=action.action_packet_transition_event_material_v01(event)))
    event_validation = action.validate_action_packet_transition_event_v01(event, action_packet_transition_registry_profile=profile)
    assert event_validation[0], event_validation
    old_disposition = registry.idempotency_disposition_events[-1]
    binding_ids = {old.transition_evidence_binding_id: new.transition_evidence_binding_id
        for old, new in zip(old_event.transition_evidence_bindings, event.transition_evidence_bindings)}
    def refs(items):
        return tuple(event.transition_event_id if x == old_event.transition_event_id else
            receipt.artifact_id if x == context.receipt.artifact_id else
            evidence.attempt_evidence_id if x == original.attempt_evidence_id else binding_ids.get(x, x) for x in items)
    disposition = action.build_idempotency_disposition_event_v01(**{
        f.name: tuple(sorted(refs(getattr(old_disposition, f.name)))) if f.name in ('cause_transition_event_ids', 'evidence_refs')
        else getattr(old_disposition, f.name) for f in fields(old_disposition)
        if f.name not in ('idempotency_disposition_event_id', 'event_profile_version')})
    return replace(registry,
        action_packet_lifecycle_entries=registry.action_packet_lifecycle_entries[:-1] + (replace(entry,
            transition_events=entry.transition_events[:-1] + (event,)),),
        idempotency_disposition_events=registry.idempotency_disposition_events[:-1] + (disposition,),
        action_packet_fulfillment_attempt_contexts=registry.action_packet_fulfillment_attempt_contexts[:-1] + (
            replace(context, receipt=receipt, attempt_evidence=evidence),))


def report_receipt_rejection(registry, changed, case):
    forged = coherent_receipt_history(registry, changed)
    valid, reasons = action.validate_action_commit_packet_registry_v02(forged)
    assert not valid and reasons == ('action_packet_registry_fulfillment_receipt_invalid',), reasons
    emit(case, representation='REBUILT_RECEIPT_ATTEMPT_TRANSITION_DISPOSITION', actual_registry_reasons=list(reasons))
    with pytest.raises(ValueError):
        action.replay_action_packet_lifecycle_history_v01(forged,
            packet_id=registry.action_packet_lifecycle_entries[-1].root_bound_genesis.packet_identity.packet_id)


def test_s02_legacy_unchanged_neighbor_and_coherent_history_rejection():
    p = runner.authorize_and_prepare_action_v01(runner.build_legacy_payment_candidate_v01())
    _, current = runner.dispatch_prepared_action_v01(p)
    receipt = current.action_packet_fulfillment_attempt_contexts[-1].receipt
    plain = abi.kernel_artifact_to_plain_dict_v01(receipt)
    assert len(plain['payload']) == 19
    equivalent = rebuilt_receipt(plain, native=False)
    assert equivalent is not receipt and equivalent == receipt
    control = coherent_receipt_history(current, equivalent)
    assert control == current and action.validate_action_commit_packet_registry_v02(control) == (True, ())
    replay = action.replay_action_packet_lifecycle_history_v01(control, packet_id=p.root_bound.packet_identity.packet_id)
    assert replay.reconstructed_state.idempotency_disposition == 'CONSUMED'
    plain['payload']['future_permission_created'] = True
    report_receipt_rejection(current, rebuilt_receipt(plain, native=False), 'S02.COHERENT_HISTORY')


def test_s04_corridor_authorized_parameter_target_adapter_candidate_binding():
    p = runner.prepare_native_playback_v01()
    different = runner.prepare_native_playback_v01(device_ref='device:u1:two', content_ref='content:u1:beta')
    _, positive = runner.dispatch_prepared_action_v01(different)
    assert positive.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    step_fields = {f.name: getattr(p.corridor_step, f.name) for f in fields(p.corridor_step) if f.name != 'step_id'}
    equivalent = action.build_common_corridor_step_v01(**step_fields)
    assert equivalent is not p.corridor_step and equivalent == p.corridor_step
    def with_step(step):
        corridor = action.build_common_contract_fulfillment_corridor_v01(**{
            f.name: (step,) if f.name == 'steps' else getattr(p.corridor, f.name)
            for f in fields(p.corridor) if f.name != 'corridor_id'})
        assert action.validate_common_corridor_v01(corridor) == (True, ())
        return replace(fresh_prepared_catalogue(p), corridor=corridor, corridor_step=step)
    _, control = runner.dispatch_prepared_action_v01(with_step(equivalent))
    assert control.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    changes = {'PARAMETERS': {'effect_parameters': different.corridor_step.effect_parameters},
        'TARGET': {'target_scope': different.corridor_step.target_scope},
        'ADAPTER': {'adapter_binding': action.build_action_adapter_binding_profile_v01(**{
            f.name: 'mock_adapter:other' if f.name == 'adapter_id' else getattr(p.corridor_step.adapter_binding, f.name)
            for f in fields(p.corridor_step.adapter_binding)})},
        'CANDIDATE': {'authorization_candidate_id': different.corridor_step.authorization_candidate_id}}
    for case, change in changes.items():
        step = action.build_common_corridor_step_v01(**dict(step_fields, **change))
        assert step != equivalent
        before = mocks.observed_mock_calls_v01()
        altered = with_step(step)
        expected_reason = 'native_corridor_scope_time_expansion' if case == 'TARGET' else 'native_corridor_authorized_operation_mismatch'
        with pytest.raises(ValueError, match='^' + expected_reason + '$') as boundary:
            action.build_action_packet_effect_firewall_projection_v01(p.registry,
                packet_id=p.root_bound.packet_identity.packet_id, corridor=altered.corridor, corridor_step=step,
                current_dependency_observations=p.observations, logical_time_bridge=p.bridge,
                eligibility_evaluation_time=1014, eligibility_evaluation_time_source='u1.controlled_utc',
                eligibility_evaluation_context_id='context:u1:dispatch')
        host = runner.host_for_prepared_action_v01(altered)
        with pytest.raises(ValueError, match='^host_current_action_not_executable$'):
            host.dispatch(**dispatch_kwargs(p))
        assert mocks.observed_mock_calls_v01() == before and host.revision == 0
        emit('S04.' + case, actual_public_boundary=str(boundary.value), host_boundary='host_current_action_not_executable', executor_calls=0)
    narrowed = action.build_common_corridor_step_v01(**dict(step_fields, issued_at_utc=1011, expires_at_utc=1020))
    _, narrow_result = runner.dispatch_prepared_action_v01(with_step(narrowed))
    assert narrow_result.action_packet_fulfillment_attempt_contexts[-1].projection.expires_at_tick == action.epoch_seconds_to_logical_tick_v01(p.bridge, 1020)
    source = mocks.TrustedMockWorkSourceV01(p.observations, p.bridge, 1020, 'u1.controlled_utc', 'context:u1:dispatch')
    host = runner.host_for_prepared_action_v01(with_step(narrowed), source)
    with pytest.raises(ValueError, match='^host_current_action_not_executable$'):
        host.dispatch(**dict(dispatch_kwargs(p), evaluation_time=1020))
    emit('S04.TIME_NARROWING', accepted_at=1014, refused_at=1020)


_REENTRY_CONTROL = {}


def execute_reentry_control(invocation):
    host, prepared = _REENTRY_CONTROL['host'], _REENTRY_CONTROL['prepared']
    with pytest.raises(ValueError, match='^host_reentry_forbidden$') as error:
        host.dispatch(**dispatch_kwargs(prepared, host.revision))
    _REENTRY_CONTROL['observed'] = str(error.value)
    return mocks.execute_playback_v01(invocation)


def test_s06_reentry_during_real_dispatch_cannot_interleave():
    p = variant_prepared(execute_reentry_control)
    host = runner.host_for_prepared_action_v01(p)
    _REENTRY_CONTROL.update(host=host, prepared=p)
    try:
        start = len(mocks.observed_mock_calls_v01())
        current = host.dispatch(**dispatch_kwargs(p))
        assert _REENTRY_CONTROL['observed'] == 'host_reentry_forbidden'
        assert current.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
        assert sum(c[0] == 'EXECUTOR_STARTED' for c in mocks.observed_mock_calls_v01()[start:]) == 1
        assert host.revision == 1
        emit('S06.REENTRY', actual_rejection=_REENTRY_CONTROL['observed'], outer_outcome='CONSUMED')
    finally:
        _REENTRY_CONTROL.clear()


def variant_prepared(executor):
    canonical, _, inputs = runner.build_native_playback_candidate_v01()
    admitted = mocks.admit_playback_variant_v01('device:u1:one', 'host:u1:playback', executor)
    return runner.authorize_and_prepare_action_v01(runner.build_native_from_business_v01(canonical, admitted, inputs), admitted, inputs)


def test_s01_native_playback_two_real_inputs_receipt_and_replay():
    outputs = []
    for content in ('content:u1:alpha', 'content:u1:beta'):
        p = runner.prepare_native_playback_v01(content_ref=content)
        before = repr(p.registry)
        log_start = len(mocks.observed_mock_calls_v01())
        host, consumed = runner.dispatch_prepared_action_v01(p)
        context = consumed.action_packet_fulfillment_attempt_contexts[-1]
        assert context.attempt_evidence.outcome_class == 'CONSUMED'
        assert action.validate_action_commit_packet_registry_v02(consumed) == (True, ())
        plain = abi.kernel_artifact_to_plain_dict_v01(context.receipt)
        assert len(plain['payload']) == 21
        evidence = firewall.native_execution_evidence_from_plain_data_v01(plain['payload']['execution_evidence'])
        assert evidence.invocation.inputs == p.inputs
        assert evidence.invocation.packet_id == p.root_bound.packet_identity.packet_id
        assert evidence.result.output_validation.valid is True
        assert evidence.admission == firewall.snapshot_admitted_capability_v01(p.admitted)
        output = {r.parameter_name: r.value for r in evidence.result.output}
        assert output['content_ref'] == content
        assert output['playback_state'] == 'playing:' + content + '@device:u1:one'
        calls = mocks.observed_mock_calls_v01()[log_start:]
        assert tuple(c[0] for c in calls) == ('INPUT_VALIDATOR', 'INPUT_VALIDATOR', 'EXECUTOR_STARTED', 'OUTPUT_VALIDATOR')
        assert calls[0][2] == calls[1][2] == evidence.invocation.inputs
        assert calls[2][2] == evidence.invocation.inputs and calls[3][2] == evidence.result.output
        final = host.observe_receipt(packet_id=p.root_bound.packet_identity.packet_id,
            attempt_evidence_id=context.attempt_evidence.attempt_evidence_id, expected_revision=host.revision,
            evaluation_time=1015, evaluation_time_source='u1.controlled_utc')
        before_replay_calls = mocks.observed_mock_calls_v01()
        replay = host.replay(packet_id=p.root_bound.packet_identity.packet_id)
        assert replay.reconstructed_state.lifecycle_state == 'RECEIPT_RECEIVED'
        assert replay.reconstructed_state.idempotency_disposition == 'CONSUMED'
        assert replay.adapter_calls == 0 and not replay.creates_permission and not replay.creates_authority
        assert mocks.observed_mock_calls_v01() == before_replay_calls
        assert repr(p.registry) == before and final is not p.registry
        outputs.append(output)
        emit('S01.' + content.rsplit(':', 1)[-1], outcome=context.attempt_evidence.outcome_class,
            packet_id=p.root_bound.packet_identity.packet_id, receipt_id=context.receipt.artifact_id,
            output=output, observed_call_order=[c[0] for c in calls])
    assert outputs[0] != outputs[1]


def test_s03_both_encodings_positive_then_shared_consumed_key():
    profile = transitions.build_action_packet_transition_registry_profile_v01()
    old = runner.authorize_and_prepare_action_v01(runner.build_legacy_payment_candidate_v01())
    native = runner.authorize_and_prepare_action_v01(*runner.build_native_payment_candidate_v01())
    assert old.root_bound.canonical_projection.idempotency_identity == native.root_bound.canonical_projection.idempotency_identity
    assert old.root_bound.packet_identity != native.root_bound.packet_identity
    for first, second_kind in ((old, 'NATIVE'), (native, 'LEGACY')):
        host, current = runner.dispatch_prepared_action_v01(first)
        context = current.action_packet_fulfillment_attempt_contexts[-1]
        assert context.attempt_evidence.outcome_class == 'CONSUMED'
        payload = abi.kernel_artifact_to_plain_dict_v01(context.receipt)['payload']
        assert len(payload) == (19 if first is old else 21)
        predecessor_id = first.root_bound.packet_identity.packet_id
        if second_kind == 'NATIVE':
            c, admitted, inputs = runner.build_native_payment_candidate_v01(predecessor_packet_id=predecessor_id)
            second = runner.authorize_action_v01(c)
        else:
            second = runner.authorize_action_v01(runner.build_legacy_payment_candidate_v01(predecessor_packet_id=predecessor_id))
        assert action.validate_common_root_bound_action_commit_packet_v01(second) == (True, ())
        assert second.root_decision_projection.root_decision_result.decision == 'ACCEPT'
        assert first.root_bound.canonical_projection.idempotency_identity == second.canonical_projection.idempotency_identity
        before = repr(current)
        with pytest.raises(ValueError, match='^consumed_key_permanently_closed$') as error:
            action.record_action_packet_genesis_v01(current, root_bound_genesis=second,
                action_packet_transition_registry_profile=profile)
        assert repr(current) == before
        assert host.replay(packet_id=predecessor_id).reconstructed_state.idempotency_disposition == 'CONSUMED'
        emit('S03.' + second_kind, positive='CONSUMED', rejected=str(error.value),
            second_root_decision=second.root_decision_projection.root_decision_result.decision_id,
            key=first.root_bound.canonical_projection.idempotency_identity.idempotency_key)


def test_s03_code_only_successor_cannot_reopen_consumed():
    p = runner.authorize_and_prepare_action_v01(*runner.build_native_payment_candidate_v01())
    _, consumed = runner.dispatch_prepared_action_v01(p)
    successor = runner.authorize_action_v01(runner.build_native_payment_candidate_v01(
        executor=mocks.execute_payment_revision_v01, predecessor_packet_id=p.root_bound.packet_identity.packet_id)[0])
    left, right = p.root_bound.canonical_projection, successor.canonical_projection
    assert left.logical_intent == right.logical_intent and left.idempotency_identity == right.idempotency_identity
    assert left.execution_binding != right.execution_binding and left.authorization_candidate != right.authorization_candidate
    assert action.validate_common_root_bound_action_commit_packet_v01(successor) == (True, ())
    with pytest.raises(ValueError, match='^consumed_key_permanently_closed$') as error:
        action.record_action_packet_genesis_v01(consumed, root_bound_genesis=successor,
            action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01())
    emit('S03.CODE_SUCCESSOR', rejected=str(error.value), same_key=left.idempotency_identity.idempotency_key)


def test_s05_real_root_revocation_at_same_unexpired_time():
    p = runner.prepare_native_playback_v01()
    host = runner.host_for_prepared_action_v01(p)
    bundle = runner.build_prestart_root_revocation_v01(p)
    before_calls = mocks.observed_mock_calls_v01()
    update = hosts.accept_current_revocation_v01(host, expected_revision=0, **bundle)
    assert type(update) is tuple and len(update) == 2
    revoked, revision = update
    assert revoked is host.registry and revision == host.state_revision == 1
    assert bundle['revocation_root_projection'].root_decision_result.decision == 'ACCEPT'
    assert action.validate_action_commit_packet_registry_v02(revoked) == (True, ())
    assert host.replay(packet_id=p.root_bound.packet_identity.packet_id).reconstructed_state.lifecycle_state == 'REVOKED'
    assert p.root_bound.canonical_projection.temporal_authority.expires_at_utc > 1014
    with pytest.raises(ValueError, match='^host_current_action_not_executable$') as error:
        host.dispatch(**dispatch_kwargs(p, host.revision))
    assert mocks.observed_mock_calls_v01() == before_calls
    unchanged = runner.host_for_prepared_action_v01(fresh_prepared_catalogue(p))
    positive = unchanged.dispatch(**dispatch_kwargs(p))
    assert positive.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    emit('S05', rejected=str(error.value), same_timestamp=1014, independent_neighbor='CONSUMED',
        root_decision_id=bundle['revocation_root_projection'].root_decision_result.decision_id)


def test_s06_stale_revision_and_old_registry_are_not_authority():
    p = runner.prepare_native_playback_v01()
    host = runner.host_for_prepared_action_v01(p)
    calls = mocks.observed_mock_calls_v01()
    with pytest.raises(ValueError, match='^host_stale_revision$'):
        host.dispatch(**dispatch_kwargs(p, 1))
    with pytest.raises(TypeError):
        host.dispatch(**dispatch_kwargs(p), registry=p.registry)
    assert mocks.observed_mock_calls_v01() == calls and host.registry is p.registry
    current = host.dispatch(**dispatch_kwargs(p))
    with pytest.raises(ValueError, match='^host_stale_revision$'):
        host.dispatch(**dispatch_kwargs(p, 0))
    calls = mocks.observed_mock_calls_v01()
    old_replay = action.replay_action_packet_lifecycle_history_v01(p.registry, packet_id=p.root_bound.packet_identity.packet_id)
    assert old_replay.reconstructed_state.lifecycle_state == 'PENDING_FULFILLMENT'
    assert not old_replay.reconstructed_state.executable
    assert host.registry is current and mocks.observed_mock_calls_v01() == calls
    emit('S06', current_revision=host.revision, historical_replay_creates_permission=old_replay.creates_permission)


@pytest.mark.parametrize('executor', (mocks.execute_playback_uncertain_v01, mocks.execute_playback_wrong_output_v01))
def test_s07_started_failure_closes_key_and_blocks_free_retry(executor):
    p = variant_prepared(executor)
    start = len(mocks.observed_mock_calls_v01())
    host, result = runner.dispatch_prepared_action_v01(p)
    attempt = result.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence
    assert attempt.outcome_class == 'UNCERTAIN' and attempt.adapter_call_count == 1
    state = action.derive_action_packet_lifecycle_state_v01(result, packet_id=p.root_bound.packet_identity.packet_id)
    assert state.idempotency_disposition == 'UNCERTAIN_CLOSED'
    calls = mocks.observed_mock_calls_v01()[start:]
    assert sum(c[0].startswith('EXECUTOR_STARTED') for c in calls) == 1
    if executor is mocks.execute_playback_wrong_output_v01:
        assert calls[-1][0] == 'OUTPUT_VALIDATOR'
    before = mocks.observed_mock_calls_v01()
    with pytest.raises(ValueError, match='^host_current_action_not_executable$'):
        host.dispatch(**dispatch_kwargs(p, host.revision))
    assert mocks.observed_mock_calls_v01() == before
    clean_canonical, admitted, inputs = runner.build_native_playback_candidate_v01()
    successor = runner.authorize_action_v01(runner.build_native_from_business_v01(
        clean_canonical, admitted, inputs, predecessor_packet_id=p.root_bound.packet_identity.packet_id))
    assert successor.canonical_projection.idempotency_identity == p.root_bound.canonical_projection.idempotency_identity
    with pytest.raises(ValueError, match='^uncertain_key_permanently_closed$'):
        action.record_action_packet_genesis_v01(result, root_bound_genesis=successor,
            action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01())
    emit('S07.' + executor.__name__, outcome=attempt.outcome_class, disposition=state.idempotency_disposition,
        actual_calls=[c[0] for c in calls])


def test_s09_exact_nominal_types_ranges_and_reserved_names():
    good = firewall.build_capability_field_v01(name='count', value_type='INTEGER', required=True, consequential=False, minimum=1, maximum=3)
    value = action.build_action_effect_parameter_record_v01(parameter_name='count', value_type='INTEGER', value=2)
    assert firewall.validate_capability_values_v01((good,), (value,)) == ()
    with pytest.raises(ValueError):
        firewall.build_capability_field_v01(name='count', value_type='INTEGER', required=True, consequential=False, minimum=True)
    assert firewall.validate_capability_values_v01((good,), (replace(value, value=True),))
    assert firewall.validate_capability_values_v01((good,), ({'parameter_name':'count','value_type':'INTEGER','value':2},))
    for name in ('capability_definition_ref', 'capability_implementation_ref', 'capability_input_contract_ref', 'capability_output_contract_ref'):
        with pytest.raises(ValueError, match='^capability_reserved_field$'):
            firewall.build_capability_field_v01(name=name, value_type='REFERENCE', required=True, consequential=True)
    emit('S09.TYPES', valid_neighbor=value.value, nominal_dictionary_rejected=True, bool_as_int_rejected=True)


def test_s09_both_fresh_import_orders():
    root = Path(__file__).resolve().parents[1]
    for first, second in (('hedgehog.action_commit_packet_v02', 'hedgehog.kernel.effect_firewall_v01'),
        ('hedgehog.kernel.effect_firewall_v01', 'hedgehog.action_commit_packet_v02')):
        code = ('import importlib; importlib.import_module(' + repr(first) + '); importlib.import_module(' + repr(second) + '); '
            'from demo.work_composition_mock_capabilities_v01 import admit_playback_v01; '
            'from hedgehog.action_commit_packet_v02 import build_native_execution_binding_v01; '
            'print(build_native_execution_binding_v01(admitted_capability=admit_playback_v01("device:import", "host:import")))')
        result = subprocess.run([sys.executable, '-c', code], cwd=root, env=dict(os.environ, PYTHONPATH=str(root)),
            capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr
        assert not result.stderr and 'NativeExecutionBindingV01(' in result.stdout
        emit('S09.IMPORT.' + first, return_code=result.returncode, stdout=result.stdout)


def raw_typed_plain(value):
    """Negative-case representation, deliberately not a success serializer."""
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is tuple:
        return [raw_typed_plain(v) for v in value]
    assert is_dataclass(value)
    return {f.name: raw_typed_plain(getattr(value, f.name)) for f in fields(value)}


def test_s08_retained_receipt_actual_output_context_and_downgrade_controls():
    p = runner.prepare_native_playback_v01()
    _, current = runner.dispatch_prepared_action_v01(p)
    context = current.action_packet_fulfillment_attempt_contexts[-1]
    plain = abi.kernel_artifact_to_plain_dict_v01(context.receipt)
    evidence = firewall.native_execution_evidence_from_plain_data_v01(plain['payload']['execution_evidence'])
    equivalent = rebuilt_receipt(plain, native=True)
    assert equivalent == context.receipt and equivalent is not context.receipt
    control = coherent_receipt_history(current, equivalent)
    assert control == current and action.validate_action_commit_packet_registry_v02(control) == (True, ())
    assert firewall.validate_retained_native_effect_receipt_v01(receipt=equivalent,
        request=context.request, decision=context.decision) == ()
    cases = {}
    missing = copy.deepcopy(plain)
    del missing['payload']['execution_evidence']
    cases['MISSING_EVIDENCE'] = missing
    downgrade = copy.deepcopy(missing)
    del downgrade['payload']['receipt_profile']
    cases['DOWNGRADE_BOTH_KEYS'] = downgrade
    extra = copy.deepcopy(plain)
    extra['payload']['invented_success'] = True
    cases['EXTRA_FIELD'] = extra
    nested_extra = copy.deepcopy(plain)
    nested_extra['payload']['execution_evidence']['result']['invented_success'] = True
    cases['EXTRA_NESTED_FIELD'] = nested_extra
    permission = copy.deepcopy(plain)
    permission['payload']['future_permission_created'] = True
    cases['PERMISSION_CREATION'] = permission
    # Change output with a fresh, actual designated negative validation result.
    output = tuple(replace(v, value='stopped') if v.parameter_name == 'playback_state' else v for v in evidence.result.output)
    negative = p.admitted.output_validator(p.admitted.definition, evidence.invocation, output)
    assert not negative.valid and negative.reason_codes
    altered_result = reidentify_native(replace(evidence.result, output=output, output_validation=negative),
        'capability_result', 'result_id')
    assert firewall.validate_capability_execution_result_v01(altered_result, evidence.invocation,
        evidence.admission) == ('capability_output_validation_failed',)
    bad_output = copy.deepcopy(plain)
    bad_output['payload']['execution_evidence'] = raw_typed_plain(replace(evidence, result=altered_result))
    cases['ACTUAL_NEGATIVE_OUTPUT'] = bad_output
    missing_output = copy.deepcopy(plain)
    missing_output['payload']['execution_evidence']['result']['output'] = None
    cases['MISSING_OUTPUT'] = missing_output
    for field, value in (('packet_id', 'packet:foreign'), ('execution_attempt_id', 'attempt:foreign'),
        ('candidate_id', 'candidate:foreign')):
        invocation = reidentify_native(replace(evidence.invocation, **{field: value}), 'capability_invocation', 'invocation_id')
        assert firewall.validate_bound_capability_invocation_v01(invocation, evidence.admission) == ()
        validation = p.admitted.output_validator(p.admitted.definition, invocation, evidence.result.output)
        assert validation.valid
        result = reidentify_native(replace(evidence.result, invocation_id=invocation.invocation_id,
            execution_attempt_id=invocation.execution_attempt_id, output_validation=validation), 'capability_result', 'result_id')
        foreign = replace(evidence, invocation=invocation, result=result)
        assert firewall.validate_native_execution_evidence_v01(foreign) == ()
        changed = copy.deepcopy(plain)
        changed['payload']['execution_evidence'] = firewall.native_execution_evidence_to_plain_data_v01(foreign)
        cases['FOREIGN_' + field.upper()] = changed
    other = runner.prepare_native_playback_v01(content_ref='content:u1:other')
    _, other_current = runner.dispatch_prepared_action_v01(other)
    other_plain = abi.kernel_artifact_to_plain_dict_v01(other_current.action_packet_fulfillment_attempt_contexts[-1].receipt)
    foreign_source = copy.deepcopy(plain)
    foreign_source['payload']['execution_evidence'] = other_plain['payload']['execution_evidence']
    cases['FOREIGN_GENUINE_EXECUTION'] = foreign_source
    before_calls = mocks.observed_mock_calls_v01()
    for case, changed in cases.items():
        receipt = rebuilt_receipt(changed, native=True)
        assert not abi.validate_kernel_artifact_v01(receipt)
        report_receipt_rejection(current, receipt, 'S08.' + case)
    replay = action.replay_action_packet_lifecycle_history_v01(current, packet_id=p.root_bound.packet_identity.packet_id)
    assert replay.reconstructed_state.idempotency_disposition == 'CONSUMED'
    assert mocks.observed_mock_calls_v01() == before_calls
    emit('S08.REPLAY', current_or_old_business_code_calls=0, historical_disposition='CONSUMED',
        negative_output_reason=list(negative.reason_codes))


def test_s08_live_admission_is_not_a_copied_hash_or_changed_callable():
    p = runner.prepare_native_playback_v01()
    assert firewall.validate_admitted_capability_v01(p.admitted) == ()
    unchanged_copy = replace(p.admitted)
    assert unchanged_copy == p.admitted and unchanged_copy is not p.admitted
    assert firewall.validate_admitted_capability_v01(unchanged_copy) == ('capability_not_trusted_admission',)
    for changed in (replace(p.admitted, executor=mocks.execute_playback_wrong_output_v01),
        replace(p.admitted, catalogue_revision=p.admitted.catalogue_revision + 1)):
        assert firewall.validate_admitted_capability_v01(changed) == ('capability_not_trusted_admission',)
    genuine_new = mocks.admit_playback_v01('device:u1:one', 'host:u1:playback')
    assert genuine_new is not p.admitted and firewall.validate_admitted_capability_v01(genuine_new) == ()
    snapshot = firewall.snapshot_admitted_capability_v01(genuine_new)
    assert snapshot == firewall.snapshot_admitted_capability_v01(p.admitted)
    _, positive = runner.dispatch_prepared_action_v01(replace(p, admitted=genuine_new))
    assert positive.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    emit('S08.ADMISSION', copied_snapshot_is_not_live_authority=True, genuine_reobserved_neighbor='CONSUMED')


def test_s08_changed_code_requires_its_own_actual_root_authorization():
    original = runner.authorize_and_prepare_action_v01(*runner.build_native_payment_candidate_v01())
    canonical, admitted, inputs = runner.build_native_payment_candidate_v01(executor=mocks.execute_payment_revision_v01)
    old = original.root_bound.canonical_projection
    assert canonical.idempotency_identity == old.idempotency_identity
    assert canonical.execution_binding != old.execution_binding
    assert not firewall.validate_capability_business_binding_v01(admitted.definition, inputs, old)
    with pytest.raises(ValueError, match='^capability_invocation_candidate_binding$') as error:
        firewall.build_bound_capability_invocation_v01(admitted_capability=admitted,
            task_id='task:changed_code', work_instance_id='work:changed_code', owning_root_id=old.owning_local_root_id,
            candidate_id=old.authorization_candidate.root_packet_authorization_candidate_id,
            packet_id=original.root_bound.packet_identity.packet_id, execution_attempt_id='attempt:changed_code',
            inputs=inputs, resource_refs=admitted.definition.resource_refs, canonical_projection=old)
    fresh = runner.authorize_and_prepare_action_v01(canonical, admitted, inputs)
    _, actual = runner.dispatch_prepared_action_v01(fresh)
    assert actual.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    emit('S08.CODE', actual_rejection=str(error.value), reauthorized_neighbor='CONSUMED')


def test_host_public_inspection_and_pure_work_cannot_dispatch_an_effect():
    p = runner.prepare_native_playback_v01()
    admitted = mocks.admit_playback_plan_v01('host:u1:plan')
    host = hosts.build_root_work_execution_host_v01(owning_root_id=p.root_bound.canonical_projection.owning_local_root_id,
        registry=p.registry, catalogue=(p.admitted, admitted), packet_bindings=((p.root_bound.packet_identity.packet_id,
            p.corridor, p.corridor_step, p.admitted.admission_id, p.inputs),),
        current_dependency_observations=p.observations, logical_time_bridge=p.bridge,
        trusted_source=mocks.TrustedMockWorkSourceV01(p.observations, p.bridge, 1014,
            'u1.controlled_utc', 'context:u1:dispatch'))
    query = dispatch_kwargs(p)
    query.pop('task_id')
    inspection = hosts.inspect_current_action_v01(host, **query)
    assert inspection.present_executable and host.state_revision == 0
    baseline = host.registry
    invocation, result, revision = hosts.execute_admitted_pure_work_v01(host, admission_id=admitted.admission_id,
        task_id='task:plan', work_instance_id='work:plan', inputs=p.inputs, expected_revision=0)
    assert invocation.packet_id is None and invocation.candidate_id is None
    assert result.output[0].value == 'would_play:content:u1:alpha@device:u1:one'
    assert result.output_validation.valid and host.state_revision == revision == 1 and host.registry is baseline
    assert firewall.validate_capability_execution_result_v01(result, invocation,
        firewall.snapshot_admitted_capability_v01(admitted)) == ()
    with pytest.raises(ValueError, match='^host_consequential_as_pure$'):
        hosts.execute_admitted_pure_work_v01(host, admission_id=p.admitted.admission_id, task_id='task:bad_pure',
            work_instance_id='work:bad_pure', inputs=p.inputs, expected_revision=1)
    assert host.registry is baseline and host.state_revision == 1
    emit('HOST.PURE_BOUNDARY', actual_plan=result.output[0].value, packet_or_permission_created=False,
        root_registry_unchanged=True, rejected='host_consequential_as_pure')


def test_s08_live_issuer_reconciles_actual_execution_not_just_receipt_hash(monkeypatch):
    observed = []
    real_execute = firewall.execute_bound_effect_v01
    def observe_actual_boundary(**kwargs):
        receipt = real_execute(**kwargs)
        observed.append((kwargs, receipt))
        return receipt
    monkeypatch.setattr(firewall, 'execute_bound_effect_v01', observe_actual_boundary)
    p = runner.prepare_native_playback_v01()
    _, result = runner.dispatch_prepared_action_v01(p)
    assert len(observed) == 1
    kwargs, receipt = observed[0]
    assert receipt is result.action_packet_fulfillment_attempt_contexts[-1].receipt
    context = {k: kwargs[k] for k in ('firewall', 'request', 'decision')}
    assert firewall.validate_native_effect_receipt_v01(**context, receipt=receipt) == ()
    plain = abi.kernel_artifact_to_plain_dict_v01(receipt)
    unchanged = rebuilt_receipt(plain, native=True)
    assert unchanged == receipt and unchanged is not receipt
    assert firewall.validate_native_effect_receipt_v01(**context, receipt=unchanged) == ()
    del plain['payload']['receipt_profile']
    del plain['payload']['execution_evidence']
    downgraded = rebuilt_receipt(plain, native=False)
    assert downgraded.artifact_id == receipt.artifact_id
    actual = firewall.validate_effect_receipt_v01(**context, receipt=downgraded)
    assert actual == ('effect_receipt_execution_evidence_mismatch',)
    before = mocks.observed_mock_calls_v01()
    with pytest.raises(ValueError):
        real_execute(**kwargs)
    assert mocks.observed_mock_calls_v01() == before
    emit('S08.LIVE_ISSUER', actual_reason=list(actual), repeated_executor_calls=0,
        observation='SPY_CALLED_ORIGINAL_UNCHANGED_RETURN')


def test_public_report_freshness_nonmutation_and_complete_projection():
    first = runner.collect_action_packet_portability_v01()
    before = repr(first)
    calls = mocks.observed_mock_calls_v01()
    assert runner.validate_action_packet_portability_report_v01(first) == (True, ())
    plain_a = runner.action_packet_portability_report_to_plain_data_v01(first)
    render_a = runner.render_action_packet_portability_v01(first)
    assert repr(first) == before and mocks.observed_mock_calls_v01() == calls
    second = runner.collect_action_packet_portability_v01()
    assert first is not second and first.cases is not second.cases
    assert all(a.prepared is not b.prepared and a.consumed_registry is not b.consumed_registry and
        a.receipt_registry is not b.receipt_registry for a, b in zip(first.cases, second.cases))
    assert plain_a == runner.action_packet_portability_report_to_plain_data_v01(second)
    assert render_a == runner.render_action_packet_portability_v01(second)
    assert render_a.endswith('\n') and not render_a.endswith('\n\n')
    assert json.loads(render_a) == plain_a
    assert json.dumps(plain_a, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n' == render_a
    altered = replace(first, cases=first.cases[:-1])
    assert runner.validate_action_packet_portability_report_v01(altered) == (False, ('portability_case_set',))
    swapped = replace(first.cases[0], consumed_registry=first.cases[1].consumed_registry)
    assert not runner.validate_action_packet_portability_report_v01(replace(first, cases=(swapped,) + first.cases[1:]))[0]
    emit('REPORT.FRESH', cases=len(first.cases), nonmutation=True, actual_calls_during_validation=0,
        render_bytes=len(render_a.encode()))


def validation_prepared_v03(validator, content_ref='content:u1:alpha'):
    c, old, inputs = runner.build_native_playback_candidate_v01(content_ref=content_ref)
    d = old.definition
    source = hosts.observe_local_capability_code_v01(validator)
    definition = firewall.build_capability_definition_v01(**dict({f.name: getattr(d, f.name) for f in fields(d)
        if f.name not in ('definition_id', 'contract_sha256')}, input_validator_ref=source.public_symbol,
        code_sha256s=tuple((source.public_symbol, source.source_sha256) if name == d.input_validator_ref else (name, sha)
            for name, sha in d.code_sha256s)))
    admitted = hosts.admit_local_capability_v01(definition=definition, input_validator=validator,
        output_validator=old.output_validator, executor=old.executor, catalogue_revision=0,
        host_instance_ref='host:u1:input_validation_v03')
    return runner.authorize_and_prepare_action_v01(runner.build_native_from_business_v01(c, admitted, inputs), admitted, inputs)


def public_action_context_v03(p):
    return dict(packet_id=p.root_bound.packet_identity.packet_id, corridor=p.corridor, corridor_step=p.corridor_step,
        current_dependency_observations=p.observations, logical_time_bridge=p.bridge,
        eligibility_evaluation_time=p.root_bound.canonical_projection.evaluation_time + 4,
        eligibility_evaluation_time_source='u1.controlled_utc', eligibility_evaluation_context_id='context:u1:dispatch')


def public_invocation_v03(p, claimed_evidence=None):
    projection = action.build_action_packet_effect_firewall_projection_v01(p.registry, **public_action_context_v03(p))
    c = p.root_bound.canonical_projection
    snapshot = firewall.snapshot_admitted_capability_v01(p.admitted)
    kwargs = dict(task_id='task:u1:input_validation_v03', work_instance_id='work:u1:input_validation_v03',
        owning_root_id=c.owning_local_root_id, candidate_id=c.authorization_candidate.root_packet_authorization_candidate_id,
        packet_id=projection.packet_id, execution_attempt_id=projection.execution_attempt_id,
        inputs=p.inputs, resource_refs=snapshot.definition.resource_refs)
    if claimed_evidence is None:
        return firewall.build_bound_capability_invocation_v01(admitted_capability=p.admitted, canonical_projection=c, **kwargs)
    value = firewall.BoundCapabilityInvocationV01(invocation_id='', admission_id=snapshot.admission_id,
        definition_id=snapshot.definition.definition_id, input_validation=claimed_evidence, **kwargs)
    value = reidentify_native(value, 'capability_invocation', 'invocation_id')
    assert firewall.validate_bound_capability_invocation_v01(value, snapshot, c) == ()
    return value


def claimed_input_success_v03(p, copied=None):
    # This is deliberately caller-authored test data, never evidence of a call.
    return firewall.build_capability_validation_evidence_v01(definition=p.admitted.definition, values=p.inputs,
        invocation_id=None, valid=True if copied is None else copied.valid,
        reason_codes=() if copied is None else copied.reason_codes)


def execute_public_action_v03(p, invocation):
    return action.execute_action_packet_mock_fulfillment_v01(p.registry, **public_action_context_v03(p),
        action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01(),
        admitted_capability=p.admitted, invocation=invocation)


def public_firewall_context_v03(p, invocation):
    projection = action.build_action_packet_effect_firewall_projection_v01(p.registry, **public_action_context_v03(p))
    root = p.root_bound.root_decision_projection
    root_args = dict(root_decision_kernel=root.root_decision_kernel, decision_input=root.root_decision_input,
        root_decision_result=root.root_decision_result)
    fw = firewall.build_effect_firewall_v01(**root_args, invocation_id=projection.execution_attempt_id,
        allowed_adapter_ids=projection.allowed_adapter_ids, allowed_action_kinds=projection.allowed_action_kinds,
        root_scope_refs=projection.root_scope_refs, maximum_expires_at_tick=projection.maximum_expires_at_tick)
    request = firewall.build_effect_request_v01(**root_args, request_kind=projection.request_kind,
        adapter_id=projection.adapter_id, action_kind=projection.action_kind, scope_refs=projection.scope_refs,
        issued_at_tick=projection.issued_at_tick, expires_at_tick=projection.expires_at_tick, idempotency_key=projection.idempotency_key)
    decision = firewall.authorize_effect_request_v01(firewall=fw, request=request, current_tick=projection.current_tick)
    assert decision.decision == 'ALLOW_MOCK_EFFECT'
    assert firewall.validate_effect_firewall_decision_v01(firewall=fw, request=request, decision=decision) == ()
    firewall.bind_native_action_authorization_v01(firewall=fw, registry=p.registry, projection=projection,
        corridor=p.corridor, corridor_step=p.corridor_step, current_dependency_observations=p.observations, logical_time_bridge=p.bridge)
    temporal = p.root_bound.canonical_projection.temporal_authority
    timestamp = action.format_utc_timestamp_v01
    envelope = dict(ct_session_anchor=projection.eligibility_evaluation_context_id,
        et_observed_at=timestamp(projection.eligibility_evaluation_time), freshness_class='real_time',
        kt_asof=timestamp(projection.eligibility_evaluation_time), pt_created_at=timestamp(temporal.issued_at_utc),
        ttl_seconds=temporal.expires_at_utc - projection.eligibility_evaluation_time,
        valid_from=timestamp(temporal.issued_at_utc), valid_to=timestamp(temporal.expires_at_utc))
    return dict(firewall=fw, request=request, decision=decision, current_tick=projection.current_tick,
        invocation=invocation, admitted_capability=p.admitted, child_scope_refs=projection.scope_refs,
        child_expires_at_tick=projection.expires_at_tick, time_envelope=envelope)


class CapabilityCallObservationV03:
    """Read-only CPython call/return observation; no callable replacement."""
    def __init__(self, admitted):
        self.code_objects = (admitted.input_validator.__code__, admitted.executor.__code__, admitted.output_validator.__code__)
        self.codes = {id(admitted.input_validator.__code__): 'input', id(admitted.executor.__code__): 'executor',
            id(admitted.output_validator.__code__): 'output'}
        self.events = []
        self.input_arguments = []

    def observe(self, frame, event, value):
        kind = self.codes.get(id(frame.f_code))
        if kind is not None and event in ('call', 'return'):
            self.events.append((kind, event, value if event == 'return' else None))
            if kind == 'input' and event == 'call':
                self.input_arguments.append((frame.f_locals['definition'], frame.f_locals['inputs']))

    def __enter__(self):
        self.previous = sys.getprofile()
        sys.setprofile(self.observe)
        return self

    def __exit__(self, *exc):
        sys.setprofile(self.previous)

    def calls(self, kind):
        return sum(k == kind and e == 'call' for k, e, _ in self.events)

    def returns(self, kind):
        return tuple(v for k, e, v in self.events if k == kind and e == 'return')


def validate_playback_alpha_only_v03(definition, inputs):
    rejected = any(v.parameter_name == 'content_ref' and v.value != 'content:u1:alpha' for v in inputs)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs, invocation_id=None,
        valid=not rejected, reason_codes=('controlled_beta_refusal',) if rejected else ())


def validate_playback_input_exception_v03(definition, inputs):
    raise RuntimeError('controlled_input_validator_exception')


def validate_playback_input_wrong_type_v03(definition, inputs):
    return {'valid': True, 'reason_codes': ()}


def validate_playback_input_foreign_subject_v03(definition, inputs):
    other = tuple(action.build_action_effect_parameter_record_v01(parameter_name=v.parameter_name,
        value_type=v.value_type, value='content:u1:foreign') if v.parameter_name == 'content_ref' else v for v in inputs)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=other,
        invocation_id=None, valid=True, reason_codes=())


def validate_playback_input_foreign_code_v03(definition, inputs):
    actual = firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=True, reason_codes=())
    return replace(actual, validator_code_sha256=dict(definition.code_sha256s)[definition.output_validator_ref])


def assert_prestart_v03(p, observation, before, boundary=None):
    assert observation.calls('input') == 1 and observation.calls('executor') == observation.calls('output') == 0
    assert len(observation.input_arguments) == 1
    assert observation.input_arguments[0][0] is p.admitted.definition and observation.input_arguments[0][1] is p.inputs
    assert repr(p.registry) == before and action.validate_action_commit_packet_registry_v02(p.registry) == (True, ())
    assert p.registry.action_packet_fulfillment_attempt_contexts == ()
    assert action.derive_action_packet_lifecycle_state_v01(p.registry,
        packet_id=p.root_bound.packet_identity.packet_id).idempotency_disposition == 'RESERVED'
    if boundary is not None:
        counters = firewall.effect_firewall_to_plain_dict_v01(boundary)['state_counters']
        assert counters['mock_effect_execution_count'] == counters['consumed_capability_count'] == counters['terminal_receipt_count'] == 0
        assert not boundary._state.started_capability_ids


def test_i1_public_action_requires_actual_designated_input_acceptance():
    p = validation_prepared_v03(validate_playback_refused_inputs_v01)
    claimed = public_invocation_v03(p, claimed_input_success_v03(p))
    before = repr(p.registry)
    with CapabilityCallObservationV03(p.admitted) as observed:
        # A preserves its public simple-token error vocabulary; observe the actual refusal separately.
        with pytest.raises(ValueError, match='^action_packet_mock_fulfillment_invalid$') as error:
            execute_public_action_v03(p, claimed)
    assert_prestart_v03(p, observed, before)
    result, = observed.returns('input')
    assert result.valid is False and result.reason_codes == ('controlled_input_refusal',)
    with CapabilityCallObservationV03(p.admitted) as builder:
        with pytest.raises(ValueError, match='^capability_input_validation_failed:controlled_input_refusal$'):
            public_invocation_v03(p)
    assert builder.calls('input') == 1 and builder.calls('executor') == 0
    good = runner.prepare_native_playback_v01()
    with CapabilityCallObservationV03(good.admitted) as positive:
        actual_invocation = public_invocation_v03(good)
        consumed = execute_public_action_v03(good, actual_invocation)
    context = consumed.action_packet_fulfillment_attempt_contexts[-1]
    assert positive.calls('input') == 2 and positive.calls('executor') == positive.calls('output') == 1
    assert all(d is good.admitted.definition and values is good.inputs for d, values in positive.input_arguments)
    assert context.attempt_evidence.outcome_class == 'CONSUMED' and context.attempt_evidence.adapter_call_count == 1
    assert action.validate_action_commit_packet_registry_v02(consumed) == (True, ())
    emit('I1.PUBLIC_A', public_a_reason=str(error.value), actual_designated_reasons=result.reason_codes,
        rejecting_validator_calls=observed.calls('input'),
        rejecting_executor_calls=observed.calls('executor'), disposition='RESERVED', positive_input_calls=positive.calls('input'),
        positive_executor_calls=positive.calls('executor'), actual_receipt=context.receipt.artifact_id)


def test_i2_public_firewall_independently_checks_actual_input_acceptance():
    p = validation_prepared_v03(validate_playback_refused_inputs_v01)
    kwargs = public_firewall_context_v03(p, public_invocation_v03(p, claimed_input_success_v03(p)))
    before = repr(p.registry)
    with CapabilityCallObservationV03(p.admitted) as observed:
        with pytest.raises(ValueError, match='^capability_input_validation_failed:controlled_input_refusal$') as error:
            firewall.execute_bound_effect_v01(**kwargs)
    assert_prestart_v03(p, observed, before, kwargs['firewall'])
    assert observed.returns('input')[0].reason_codes == ('controlled_input_refusal',)
    good = runner.prepare_native_playback_v01()
    # An independently constructed typed invocation is legal when live validation really accepts it.
    valid = public_firewall_context_v03(good, public_invocation_v03(good, claimed_input_success_v03(good)))
    with CapabilityCallObservationV03(good.admitted) as positive:
        receipt = firewall.execute_bound_effect_v01(**valid)
    assert positive.calls('input') == positive.calls('executor') == positive.calls('output') == 1
    assert positive.input_arguments[0][0] is good.admitted.definition and positive.input_arguments[0][1] is good.inputs
    assert firewall.validate_native_effect_receipt_v01(firewall=valid['firewall'], request=valid['request'],
        decision=valid['decision'], receipt=receipt) == ()
    retained = valid['firewall']._state.native_evidence_by_capability_id[valid['decision'].capability_id]
    assert retained.invocation.input_validation is positive.returns('input')[0]
    emit('I2.PUBLIC_FIREWALL', actual_refusal=str(error.value), executor_calls=observed.calls('executor'),
        positive_executor_calls=positive.calls('executor'), actual_return_retained=True, receipt=receipt.artifact_id)


def test_i3_recomputed_success_cannot_transfer_between_actual_inputs_or_code():
    good = validation_prepared_v03(validate_playback_alpha_only_v03)
    actual = public_invocation_v03(good)
    consumed = execute_public_action_v03(good, actual)
    assert consumed.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    for label, validator, content, reason in (
        ('different_inputs', validate_playback_alpha_only_v03, 'content:u1:beta', 'controlled_beta_refusal'),
        ('different_code_admission', validate_playback_refused_inputs_v01, 'content:u1:alpha', 'controlled_input_refusal')):
        p = validation_prepared_v03(validator, content)
        transplanted = claimed_input_success_v03(p, copy.copy(actual.input_validation))
        assert transplanted != actual.input_validation
        claimed = public_invocation_v03(p, transplanted)
        before = repr(p.registry)
        with CapabilityCallObservationV03(p.admitted) as observed:
            with pytest.raises(ValueError, match='^action_packet_mock_fulfillment_invalid$') as error:
                execute_public_action_v03(p, claimed)
        assert_prestart_v03(p, observed, before)
        assert observed.returns('input')[0].reason_codes == (reason,)
        emit('I3.' + label, structural_check='ACCEPTED', public_a_reason=str(error.value),
            actual_designated_reasons=observed.returns('input')[0].reason_codes,
            input_calls=observed.calls('input'), executor_calls=observed.calls('executor'), claimed_hashes_recomputed=True)


def test_i4_actual_input_exception_and_malformed_returns_are_prestart():
    variants = ((validate_playback_input_exception_v03, RuntimeError, 'controlled_input_validator_exception'),
        (validate_playback_input_wrong_type_v03, ValueError, 'capability_validation_evidence_type'),
        (validate_playback_input_foreign_subject_v03, ValueError, 'capability_validation_evidence_binding'),
        (validate_playback_input_foreign_code_v03, ValueError, 'capability_validation_evidence_binding'))
    for validator, exception, reason in variants:
        for route in ('A', 'FIREWALL'):
            p = validation_prepared_v03(validator)
            claimed = public_invocation_v03(p, claimed_input_success_v03(p))
            kwargs = public_firewall_context_v03(p, claimed) if route == 'FIREWALL' else None
            expected_exception = exception if route == 'FIREWALL' else ValueError
            expected_reason = 'action_packet_mock_fulfillment_invalid' if route == 'A' and exception is RuntimeError else reason
            before = repr(p.registry)
            with CapabilityCallObservationV03(p.admitted) as observed:
                with pytest.raises(expected_exception, match='^' + expected_reason + '$') as error:
                    firewall.execute_bound_effect_v01(**kwargs) if kwargs else execute_public_action_v03(p, claimed)
            assert_prestart_v03(p, observed, before, kwargs['firewall'] if kwargs else None)
            emit('I4.' + route + '.' + validator.__name__, actual_refusal=str(error.value),
                actual_input_calls=observed.calls('input'), executor_calls=observed.calls('executor'), disposition='RESERVED')
    neighbor = runner.prepare_native_playback_v01(content_ref='content:u1:independent')
    positive = execute_public_action_v03(neighbor, public_invocation_v03(neighbor))
    assert positive.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence.outcome_class == 'CONSUMED'
    emit('I4.INDEPENDENT', outcome='CONSUMED', poststart_contrast_node='test_n03_started_interrupt_and_post_result_escape_remain_closed_in_same_host')


def test_i5_historical_native_and_legacy_evidence_never_calls_live_validators():
    for native in (False, True):
        p = runner.prepare_native_playback_v01() if native else runner.authorize_and_prepare_action_v01(runner.build_legacy_payment_candidate_v01())
        _, consumed = runner.dispatch_prepared_action_v01(p)
        context = consumed.action_packet_fulfillment_attempt_contexts[-1]
        plain = abi.kernel_artifact_to_plain_dict_v01(context.receipt)
        assert len(plain['payload']) == (21 if native else 19)
        observer = p.admitted if native else mocks.admit_playback_v01('device:u1:one', 'host:u1:historical_observer')
        before = repr(consumed)
        calls = mocks.observed_mock_calls_v01()
        with CapabilityCallObservationV03(observer) as observation:
            replay = action.replay_action_packet_lifecycle_history_v01(consumed, packet_id=p.root_bound.packet_identity.packet_id)
            assert action.validate_action_packet_lifecycle_replay_report_v01(replay, consumed,
                packet_id=p.root_bound.packet_identity.packet_id) == (True, ())
            if native:
                evidence = firewall.native_execution_evidence_from_plain_data_v01(plain['payload']['execution_evidence'])
                assert firewall.validate_native_execution_evidence_v01(evidence) == ()
                assert firewall.validate_bound_capability_invocation_v01(evidence.invocation, evidence.admission) == ()
                assert firewall.validate_retained_native_effect_receipt_v01(receipt=context.receipt,
                    request=context.request, decision=context.decision) == ()
        assert observation.events == [] and mocks.observed_mock_calls_v01() == calls and repr(consumed) == before
        assert replay.reconstructed_state.idempotency_disposition == 'CONSUMED' and replay.adapter_calls == 0
        assert abi.kernel_artifact_to_plain_dict_v01(context.receipt) == plain
        emit('I5.' + ('NATIVE' if native else 'LEGACY'), payload_keys=len(plain['payload']),
            live_input_output_executor_calls=0, receipt_identity=context.receipt.artifact_id, disposition='CONSUMED')
