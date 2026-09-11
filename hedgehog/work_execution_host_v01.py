"""One-Root current-state owner for admitted, offline action execution.

Trusted setup installs immutable packet inputs and a catalogue. Public dispatch
accepts IDs and a revision, never a caller-selected historical registry.
"""
from threading import RLock
from dataclasses import dataclass, replace
import hashlib
import inspect
from pathlib import Path
import sys
import types
from hedgehog import action_commit_packet_v02 as action
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import transition_registry_v01 as transitions


@dataclass(frozen=True)
class TrustedWorkSourceSnapshotV01:
    observations: tuple
    logical_time_bridge: object
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    source_revision: int


@dataclass(frozen=True)
class ObservedWorkAttemptV01:
    task_id: str
    work_instance_id: str
    admission_id: str
    inputs: tuple
    invocation: object
    result: object
    disposition: str
    reason: str | None


@dataclass(frozen=True)
class WorkTaskPolicyV01:
    task_id: str
    owning_root_id: str
    host_instance_ref: str
    initial_revision_id: str
    intent_ref: str
    source_ref: str
    definition_ids: tuple[str, ...]
    review_definition_ids: tuple[str, ...]
    resource_refs: tuple[str, ...]
    max_items: int
    max_compute_units: int
    max_children: int
    max_model_calls: int
    max_revisions: int


@dataclass(frozen=True)
class WorkTaskUsageV01:
    compute_units: int
    children: int
    model_calls: int
    revisions: int
    reserved_children: int


@dataclass(frozen=True)
class WorkTaskSnapshotV01:
    policy: WorkTaskPolicyV01
    current_revision_id: str
    accepted_revision_ids: tuple[str, ...]
    terminal_history_refs: tuple[str, ...]
    usage: WorkTaskUsageV01
    outcome: str
    reason: str | None
    host_revision: int


def observe_local_capability_code_v01(public_callable):
    if not (inspect.isfunction(public_callable) and public_callable.__qualname__ == public_callable.__name__
        and not public_callable.__name__.startswith('_')):
        raise ValueError('capability_public_callable')
    module = sys.modules.get(public_callable.__module__)
    if module is None or vars(module).get(public_callable.__name__) is not public_callable:
        raise ValueError('capability_loaded_callable_origin')
    path = inspect.getsourcefile(public_callable)
    if path is None or Path(path).resolve() != Path(module.__file__).resolve():
        raise ValueError('capability_source_origin')
    source = Path(path).read_bytes()
    text = source.decode('utf-8')
    if text.encode('utf-8') != source:
        raise ValueError('capability_source_utf8')
    # Observe trusted, already loaded code; compiling never executes this source.
    compiled = compile(source, path, 'exec', dont_inherit=True, optimize=sys.flags.optimize)
    matches = tuple(c for c in compiled.co_consts if type(c) is types.CodeType
        and c.co_name == public_callable.__name__)
    if len(matches) != 1 or matches[0] != public_callable.__code__:
        raise ValueError('capability_loaded_source_code_mismatch')
    return firewall.CapabilityCodeSnapshotV01(public_callable.__module__ + '.' + public_callable.__name__,
        text, hashlib.sha256(source).hexdigest())


def admit_local_capability_v01(*, definition, input_validator, output_validator,
    executor, catalogue_revision, host_instance_ref):
    sources = tuple(observe_local_capability_code_v01(c) for c in (input_validator, output_validator, executor))
    return firewall._admit_observed_capability_v01(definition=definition, input_validator=input_validator,
        output_validator=output_validator, executor=executor, catalogue_revision=catalogue_revision,
        host_instance_ref=host_instance_ref, sources=sources)


def _validate_sources(snapshot):
    if type(snapshot) is not TrustedWorkSourceSnapshotV01 or type(snapshot.source_revision) is not int or snapshot.source_revision < 0:
        raise ValueError('host_source_snapshot_invalid')
    if type(snapshot.observations) is not tuple or any(not action.validate_action_dependency_current_observation_v01(v)[0]
        for v in snapshot.observations):
        raise ValueError('host_observations_invalid')
    if not action.validate_logical_time_bridge_v01(snapshot.logical_time_bridge)[0]:
        raise ValueError('host_time_bridge_invalid')
    if type(snapshot.evaluation_time) is not int or not action.validate_signed_int64_v01(snapshot.evaluation_time)[0] or any(
        not action.validate_identity_text_v01(v)[0] for v in (snapshot.evaluation_time_source, snapshot.evaluation_context_id)):
        raise ValueError('host_trusted_time_invalid')


class RootWorkExecutionHostV01:
    __slots__ = ('_root_id', '_registry', '_catalogue', '_bindings', '_observations',
        '_bridge', '_revision', '_lock', '_active', '_events', '_source', '_source_snapshot', '_inflight', '_completed_work', '_work_attempts',
        '_task_policies', '_tasks', '_task_dispatch', '_catalogue_history', '_pure_permissions',
        '_pure_usage', '_pure_proposals', '_pure_attempts', '_pure_pending', '_pure_packages',
        '_pure_resolutions', '_pure_guest_runs', '_pure_guest_evidence')

    def __init__(self, *, owning_root_id, registry, catalogue, packet_bindings,
        current_dependency_observations, logical_time_bridge, trusted_source, task_policies=(), pure_need_permissions=()):
        valid, reasons = action.validate_action_commit_packet_registry_v02(registry)
        if not valid:
            raise ValueError(reasons[0])
        if type(owning_root_id) is not str or any(e.root_bound_genesis.canonical_projection.owning_local_root_id
            != owning_root_id for e in registry.action_packet_lifecycle_entries):
            raise ValueError('host_foreign_root')
        if type(catalogue) is not tuple or type(packet_bindings) is not tuple:
            raise ValueError('host_setup_shape')
        for admitted in catalogue:
            errors = firewall.validate_admitted_capability_v01(admitted)
            if errors:
                raise ValueError(errors[0])
        if len({a.admission_id for a in catalogue}) != len(catalogue):
            raise ValueError('host_duplicate_admission')
        self._root_id = owning_root_id
        self._registry = registry
        self._catalogue = {a.admission_id: a for a in catalogue}
        self._bindings = {}
        for packet_id, corridor, step, admitted_id, inputs in packet_bindings:
            if packet_id in self._bindings:
                raise ValueError('host_duplicate_packet_binding')
            entry = next(e for e in registry.action_packet_lifecycle_entries if e.root_bound_genesis.packet_identity.packet_id == packet_id)
            canonical = entry.root_bound_genesis.canonical_projection
            if type(canonical) is action.NativeActionCommitPacketV01:
                admitted = self._catalogue[admitted_id]
                if firewall.snapshot_admitted_capability_v01(admitted) != canonical.execution_source:
                    raise ValueError('host_packet_admission_mismatch')
                errors = firewall.validate_capability_business_binding_v01(admitted.definition, inputs, canonical)
                if errors:
                    raise ValueError(errors[0])
            elif admitted_id is not None or inputs is not None:
                raise ValueError('host_legacy_typed_binding')
            self._bindings[packet_id] = (corridor, step, admitted_id, inputs)
        if type(current_dependency_observations) is not tuple or any(
            not action.validate_action_dependency_current_observation_v01(v)[0] for v in current_dependency_observations):
            raise ValueError('host_observations_invalid')
        if not action.validate_logical_time_bridge_v01(logical_time_bridge)[0]:
            raise ValueError('host_time_bridge_invalid')
        self._observations = current_dependency_observations
        self._bridge = logical_time_bridge
        self._revision = 0
        self._lock = RLock()
        self._active = False
        self._events = []
        self._inflight = {}
        self._completed_work = []
        self._work_attempts = []
        self._task_policies = {}
        self._tasks = {}
        self._task_dispatch = None
        self._catalogue_history = (catalogue,)
        self._pure_permissions = {}
        self._pure_usage = {}
        self._pure_proposals = []
        self._pure_attempts = []
        self._pure_pending = []
        self._pure_packages = {}
        self._pure_resolutions = ()
        self._pure_guest_runs = []
        self._pure_guest_evidence = []
        if type(task_policies) is not tuple:
            raise ValueError('host_task_policy_tuple')
        if task_policies:
            from hedgehog.kernel import work_composition_v01 as work
            for policy in task_policies:
                work.validate_installed_work_task_policy_v01(policy, owning_root_id=owning_root_id, catalogue=catalogue)
                if policy.task_id in self._task_policies:
                    raise ValueError('host_duplicate_task_policy')
                self._task_policies[policy.task_id] = policy
        if type(pure_need_permissions) is not tuple:
            raise ValueError('pure_permission_tuple')
        if pure_need_permissions:
            from hedgehog import capability_admission_v01 as pure
            for permission in pure_need_permissions:
                pure.validate_pure_need_permission_v01(permission)
                policy = self._task_policies.get(permission.task_id)
                if policy is None or permission.task_id in self._pure_permissions or (
                    permission.owning_root_id, permission.initial_revision_id, permission.source_ref) != (
                    self._root_id, policy.initial_revision_id, policy.source_ref):
                    raise ValueError('pure_permission_original_policy')
                self._pure_permissions[permission.task_id] = permission
                self._pure_usage[permission.task_id] = pure.PureResourceUsageV01()
        self._source = trusted_source
        snapshot = trusted_source.read_current_v01()
        _validate_sources(snapshot)
        if (snapshot.observations, snapshot.logical_time_bridge) != (self._observations, self._bridge):
            raise ValueError('host_initial_source_binding')
        self._source_snapshot = snapshot
        for admitted in catalogue:
            self._refresh_admission(admitted, initial=True)
        for admitted in catalogue:
            admitted._origin.owner = self

    @property
    def revision(self):
        return self._revision

    @property
    def state_revision(self):
        return self._revision

    @property
    def registry(self):
        return self._registry

    @property
    def events(self):
        return tuple(self._events)

    @property
    def current_sources(self):
        return self._source_snapshot

    @property
    def owning_root_id(self):
        return self._root_id

    @property
    def admitted_catalogue(self):
        return tuple(self._catalogue.values())

    @property
    def catalogue_membership_history(self):
        return self._catalogue_history

    @property
    def pure_need_resolutions(self):
        return self._pure_resolutions

    @property
    def pure_guest_evidence(self):
        return tuple(self._pure_guest_evidence)

    @property
    def pure_admission_attempts(self):
        return tuple(self._pure_attempts)

    @property
    def pure_generation_proposals(self):
        return tuple(self._pure_proposals)

    @property
    def completed_work(self):
        """Actual invocations/results retained at completion, not submitted history."""
        return tuple(self._completed_work)

    @property
    def work_attempts(self):
        """Immutable observations recorded by this host at its actual boundary."""
        return tuple(self._work_attempts)

    @property
    def unresolved_starts(self):
        return tuple(sorted(self._inflight.items()))

    def _refresh_admission(self, admitted, initial=False):
        errors = firewall.validate_admitted_capability_v01(admitted)
        if errors:
            raise ValueError(errors[0])
        if admitted._origin.owner is not (None if initial else self):
            raise ValueError('host_foreign_catalogue_origin')
        observed = tuple(sorted((observe_local_capability_code_v01(c) for c in
            (admitted.input_validator, admitted.output_validator, admitted.executor)), key=lambda s: s.public_symbol))
        if observed != admitted.observed_code_identities:
            raise ValueError('capability_current_code_changed')

    def _refresh_sources(self, evaluation_time, evaluation_time_source, evaluation_context_id):
        current = self._source.read_current_v01()
        _validate_sources(current)
        old = self._source_snapshot
        if current.source_revision < old.source_revision or current.evaluation_time < old.evaluation_time:
            raise ValueError('host_trusted_source_regression')
        if current.source_revision == old.source_revision and current != old:
            raise ValueError('host_source_revision_not_advanced')
        if current != old:
            self._source_snapshot = current
            self._observations, self._bridge = current.observations, current.logical_time_bridge
            self._revision += 1
        if (evaluation_time, evaluation_time_source, evaluation_context_id) != (
            current.evaluation_time, current.evaluation_time_source, current.evaluation_context_id):
            raise ValueError('host_task_time_not_current')

    def _record_started(self, invocation):
        entry = next(e for e in self._registry.action_packet_lifecycle_entries
            if e.root_bound_genesis.packet_identity.packet_id == invocation.packet_id)
        c = entry.root_bound_genesis.canonical_projection
        key = c.idempotency_identity.idempotency_key
        if not self._active or key in self._inflight or invocation.candidate_id != c.authorization_candidate.root_packet_authorization_candidate_id:
            raise ValueError('host_start_context_invalid')
        self._inflight[key] = invocation
        self._events.append(('EXECUTOR_STARTED', self._revision, invocation.packet_id, invocation.invocation_id))

    def _packet_observations(self, canonical):
        # A validates an exact packet-local source set, not the host's whole catalogue.
        ids = {r.dependency_id for r in canonical.dependency_candidate.dependency_records}
        return tuple(v for v in self._observations if v.dependency_id in ids)

    def _enter(self, expected_revision):
        if self._active:
            raise ValueError('host_reentry_forbidden')
        if type(expected_revision) is not int or expected_revision != self._revision:
            raise ValueError('host_stale_revision')
        self._active = True

    def dispatch(self, *, packet_id, task_id, expected_revision, evaluation_time,
        evaluation_time_source, evaluation_context_id, work_instance_id=None):
        with self._lock:
            if self._task_policies and (self._task_dispatch is None or self._task_dispatch[:2] != (task_id, work_instance_id)):
                raise ValueError('work_task_dispatch_context_required')
            self._enter(expected_revision)
            admitted = None
            invocation = result = None
            inputs = ()
            recorded = False
            instance = 'work:' + task_id if work_instance_id is None else work_instance_id
            started_before = set(self._inflight)
            try:
                self._refresh_sources(evaluation_time, evaluation_time_source, evaluation_context_id)
                if self._task_policies and task_id not in self._task_policies:
                    raise ValueError('host_task_not_configured')
                corridor, step, admitted_id, inputs = self._bindings[packet_id]
                entry = next(e for e in self._registry.action_packet_lifecycle_entries
                    if e.root_bound_genesis.packet_identity.packet_id == packet_id)
                canonical = entry.root_bound_genesis.canonical_projection
                key = canonical.idempotency_identity.idempotency_key
                if key in self._inflight:
                    raise ValueError('host_common_key_inflight_closed')
                kwargs = dict(packet_id=packet_id, corridor=corridor, corridor_step=step,
                    current_dependency_observations=self._packet_observations(canonical), logical_time_bridge=self._bridge,
                    eligibility_evaluation_time=evaluation_time, eligibility_evaluation_time_source=evaluation_time_source,
                    eligibility_evaluation_context_id=evaluation_context_id,
                    action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01())
                inspection = action.inspect_action_packet_present_eligibility_v01(self._registry, packet_id=packet_id,
                    corridor=corridor, corridor_step=step, current_dependency_observations=kwargs['current_dependency_observations'],
                    logical_time_bridge=self._bridge, evaluation_time=evaluation_time,
                    evaluation_time_source=evaluation_time_source, evaluation_context_id=evaluation_context_id,
                    action_packet_transition_registry_profile=kwargs['action_packet_transition_registry_profile'])
                if not inspection.present_executable:
                    raise ValueError('host_current_action_not_executable')
                if task_id in self._task_policies:
                    from hedgehog.kernel import work_composition_v01 as work
                    work._charge_task_dispatch_v01(self, task_id, instance, admitted_id, inputs)
                if admitted_id is not None:
                    admitted = self._catalogue[admitted_id]
                    self._refresh_admission(admitted)
                    invocation = firewall.build_bound_capability_invocation_v01(admitted_capability=admitted,
                        task_id=task_id, work_instance_id='work:' + task_id if work_instance_id is None else work_instance_id, owning_root_id=self._root_id,
                        candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,
                        packet_id=packet_id, execution_attempt_id=entry.transition_events[-1].execution_attempt_id,
                        inputs=inputs, resource_refs=admitted.definition.resource_refs, canonical_projection=canonical)
                    kwargs.update(admitted_capability=admitted, invocation=invocation)
                    admitted._origin.start_observer = self._record_started
                self._events.append(('DISPATCH_REQUESTED', self._revision, packet_id, task_id))
                proposed = action.execute_action_packet_mock_fulfillment_v01(self._registry, **kwargs)
                valid, reasons = action.validate_action_commit_packet_registry_v02(proposed)
                if not valid:
                    raise ValueError('host_outcome_registry_invalid:' + repr(reasons))
                self._registry = proposed
                self._revision += 1
                if admitted is not None:
                    receipt = proposed.action_packet_fulfillment_attempt_contexts[-1].receipt
                    if receipt is not None:
                        from hedgehog.kernel import abi_v01 as abi
                        payload = abi.kernel_artifact_to_plain_dict_v01(receipt)['payload']
                        evidence = firewall.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])
                        self._completed_work.append((evidence.invocation, evidence.result))
                        result = evidence.result
                attempt = proposed.action_packet_fulfillment_attempt_contexts[-1].attempt_evidence
                if admitted is not None:
                    disposition = ('COMPLETED' if result is not None and result.outcome == 'SUCCEEDED'
                        else 'UNCERTAIN_CLOSED' if attempt.outcome_class in ('CONSUMED', 'UNCERTAIN')
                        else 'FAILED_NON_CONSUMING')
                    self._work_attempts.append(ObservedWorkAttemptV01(task_id, instance, admitted.admission_id,
                        inputs, invocation, result, disposition, None if disposition == 'COMPLETED' else attempt.reason_code))
                    recorded = True
                if attempt.outcome_class in ('CONSUMED', 'UNCERTAIN'):
                    self._inflight.pop(key, None)
                self._events.append(('DISPATCH_OUTCOME', self._revision, packet_id, attempt.outcome_class,
                    attempt.reason_code, attempt.adapter_call_count))
                return proposed
            except BaseException as exc:
                if admitted is not None and not recorded:
                    unresolved = set(self._inflight) != started_before
                    self._work_attempts.append(ObservedWorkAttemptV01(task_id, instance, admitted.admission_id,
                        inputs, invocation, result, 'UNCERTAIN_CLOSED' if unresolved else 'FAILED_NON_CONSUMING',
                        str(exc) if isinstance(exc, ValueError) else type(exc).__name__))
                if set(self._inflight) != started_before:
                    self._revision += 1
                    self._events.append(('STARTED_OUTCOME_UNRESOLVED', self._revision, packet_id, type(exc).__name__))
                raise
            finally:
                if admitted is not None and admitted._origin.owner is self:
                    admitted._origin.start_observer = None
                self._active = False

    def observe_receipt(self, *, packet_id, attempt_evidence_id, expected_revision,
        evaluation_time, evaluation_time_source):
        with self._lock:
            self._enter(expected_revision)
            try:
                self._registry = action.observe_action_packet_effect_receipt_v01(self._registry, packet_id=packet_id,
                    attempt_evidence_id=attempt_evidence_id, receipt_evaluation_time=evaluation_time,
                    receipt_evaluation_time_source=evaluation_time_source,
                    action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01())
                self._revision += 1
                return self._registry
            finally:
                self._active = False

    def replay(self, *, packet_id):
        with self._lock:
            return action.replay_action_packet_lifecycle_history_v01(self._registry, packet_id=packet_id)

    def apply_revocation(self, *, packet_id, expected_revision, revocation_candidate,
        revocation_root_projection, accepted_revocation_binding, invalidation_evidence, transition_event):
        with self._lock:
            self._enter(expected_revision)
            try:
                self._registry = action.record_action_packet_revocation_v01(self._registry, packet_id=packet_id,
                    revocation_candidate=revocation_candidate, revocation_root_projection=revocation_root_projection,
                    accepted_revocation_binding=accepted_revocation_binding, invalidation_evidence=invalidation_evidence,
                    transition_event=transition_event,
                    action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01())
                self._revision += 1
                self._events.append(('ROOT_REVOCATION', self._revision, packet_id,
                    revocation_root_projection.root_decision_result.decision_id))
                return self._registry
            finally:
                self._active = False


def build_root_work_execution_host_v01(*, owning_root_id, registry, catalogue, packet_bindings,
    current_dependency_observations, logical_time_bridge, trusted_source, task_policies=(), pure_need_permissions=()):
    return RootWorkExecutionHostV01(owning_root_id=owning_root_id, registry=registry, catalogue=catalogue,
        packet_bindings=packet_bindings, current_dependency_observations=current_dependency_observations,
        logical_time_bridge=logical_time_bridge, trusted_source=trusted_source, task_policies=task_policies,
        pure_need_permissions=pure_need_permissions)


def dispatch_current_action_v01(host, *, packet_id, task_id, expected_revision, evaluation_time,
    evaluation_time_source, evaluation_context_id, work_instance_id=None):
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        evidence = host.dispatch(packet_id=packet_id, task_id=task_id, expected_revision=expected_revision,
            evaluation_time=evaluation_time, evaluation_time_source=evaluation_time_source,
            evaluation_context_id=evaluation_context_id, work_instance_id=work_instance_id)
        return evidence, host.state_revision


def accept_current_revocation_v01(host, *, packet_id, expected_revision, revocation_candidate,
    revocation_root_projection, accepted_revocation_binding, invalidation_evidence, transition_event):
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        evidence = host.apply_revocation(packet_id=packet_id, expected_revision=expected_revision,
            revocation_candidate=revocation_candidate, revocation_root_projection=revocation_root_projection,
            accepted_revocation_binding=accepted_revocation_binding, invalidation_evidence=invalidation_evidence,
            transition_event=transition_event)
        return evidence, host.state_revision


def inspect_current_action_v01(host, *, packet_id, expected_revision, evaluation_time,
    evaluation_time_source, evaluation_context_id):
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        host._enter(expected_revision)
        try:
            host._refresh_sources(evaluation_time, evaluation_time_source, evaluation_context_id)
            corridor, step, admitted_id, _ = host._bindings[packet_id]
            entry = next(e for e in host._registry.action_packet_lifecycle_entries
                if e.root_bound_genesis.packet_identity.packet_id == packet_id)
            if entry.root_bound_genesis.canonical_projection.idempotency_identity.idempotency_key in host._inflight:
                raise ValueError('host_common_key_inflight_closed')
            if admitted_id is not None:
                host._refresh_admission(host._catalogue[admitted_id])
            return action.inspect_action_packet_present_eligibility_v01(host._registry, packet_id=packet_id,
                corridor=corridor, corridor_step=step,
                current_dependency_observations=host._packet_observations(entry.root_bound_genesis.canonical_projection),
                logical_time_bridge=host._bridge, evaluation_time=evaluation_time,
                evaluation_time_source=evaluation_time_source, evaluation_context_id=evaluation_context_id,
                action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01())
        finally:
            host._active = False


def execute_admitted_pure_work_v01(host, *, admission_id, task_id, work_instance_id, inputs, expected_revision):
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        if host._task_policies and host._task_dispatch != (task_id, work_instance_id, admission_id, inputs):
            raise ValueError('work_task_dispatch_context_required')
        host._enter(expected_revision)
        started = False
        invocation = result = None
        bridge_token = None
        try:
            if host._task_policies and task_id not in host._task_policies:
                raise ValueError('host_task_not_configured')
            if any(a.task_id == task_id and a.work_instance_id == work_instance_id for a in host._work_attempts):
                raise ValueError('host_work_already_attempted')
            admitted = host._catalogue[admission_id]
            host._refresh_admission(admitted)
            snapshot = firewall.snapshot_admitted_capability_v01(admitted)
            if snapshot.definition.effect_kind != 'PURE':
                raise ValueError('host_consequential_as_pure')
            if admission_id in host._pure_packages:
                from hedgehog import capability_admission_v01 as pure
                package = host._pure_packages[admission_id]
                pure.validate_admitted_pure_package_v01(package, host=host, need=package.need)
                if package.need.permission.task_id != task_id:
                    raise ValueError('pure_guest_foreign_task')
                bridge_token = pure._BRIDGE.set((host, package, task_id))
            if task_id in host._task_policies:
                from hedgehog.kernel import work_composition_v01 as work
                work._charge_task_dispatch_v01(host, task_id, work_instance_id, admission_id, inputs)
            attempt = action.build_domain_separated_identity_v01(domain='hedgehog.common_action.pure_attempt.v01',
                prefix='pure_attempt:', material=(('host', snapshot.host_instance_ref), ('root', host._root_id),
                    ('revision', host.state_revision), ('task', task_id), ('work', work_instance_id)))
            invocation = firewall.build_bound_capability_invocation_v01(admitted_capability=admitted,
                task_id=task_id, work_instance_id=work_instance_id, owning_root_id=host._root_id,
                candidate_id=None, packet_id=None, execution_attempt_id=attempt, inputs=inputs,
                resource_refs=snapshot.definition.resource_refs)
            started = True
            host._events.append(('PURE_STARTED', host._revision, invocation.invocation_id))
            output = admitted.executor(invocation)
            validation = admitted.output_validator(snapshot.definition, invocation, output)
            result = firewall.build_capability_execution_result_v01(invocation=invocation,
                admission_snapshot=snapshot, output=output, output_validation=validation)
            host._completed_work.append((invocation, result))
            if bridge_token is not None:
                runs = [r for i,p,r in host._pure_guest_runs if i is invocation and p is package]
                if len(runs) != 1:
                    raise ValueError('pure_guest_observation_count')
                host._pure_guest_evidence.append(pure.PureGuestInvocationEvidenceV01(invocation,
                    result.result_id, package.package_id, package.wasm_sha256, package.oracle_sha256, runs[0]))
            host._work_attempts.append(ObservedWorkAttemptV01(task_id, work_instance_id, admission_id,
                inputs, invocation, result, 'COMPLETED', None))
            host._events.append(('PURE_COMPLETED', host._revision + 1, result.result_id))
            return invocation, result, host._revision + 1
        except BaseException as exc:
            if not any(a.task_id == task_id and a.work_instance_id == work_instance_id for a in host._work_attempts):
                host._work_attempts.append(ObservedWorkAttemptV01(task_id, work_instance_id, admission_id,
                    inputs, invocation, result, 'UNCERTAIN_CLOSED' if started else 'FAILED_NON_CONSUMING',
                    str(exc) if isinstance(exc, ValueError) else type(exc).__name__))
            raise
        finally:
            if bridge_token is not None:
                pure._BRIDGE.reset(bridge_token)
            if started:
                host._revision += 1
            host._active = False


def reserve_pure_need_work_v01(host, *, need, kind, byte_count, expected_revision):
    """Reserve generation/admission/storage costs before trusted work begins."""
    from hedgehog import capability_admission_v01 as pure
    from hedgehog.kernel import work_composition_v01 as work
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        if type(expected_revision) is not int or expected_revision != host.state_revision or host._active:
            raise ValueError('pure_stale_host_revision')
        if kind == 'drs' and any(r.need == need for r in host._pure_resolutions):
            pure.validate_pure_need_v01(need)
            if host._pure_permissions.get(need.permission.task_id) != need.permission:
                raise ValueError('pure_drs_current_permission')
        else:
            work.validate_current_pure_need_v01(host, need=need)
        permission = host._pure_permissions[need.permission.task_id]
        usage = host._pure_usage[permission.task_id]
        if kind == 'generation':
            if usage.generation_attempts >= permission.max_generation_attempts:
                raise ValueError('pure_generation_exhausted')
            usage = replace(usage, generation_attempts=usage.generation_attempts + 1)
        elif kind == 'admission':
            if usage.admission_attempts >= permission.max_admissions:
                raise ValueError('pure_admission_exhausted')
            usage = replace(usage, admission_attempts=usage.admission_attempts + 1,
                reserved_trials=usage.reserved_trials + 256, reserved_fuel=usage.reserved_fuel + 256 * pure.worker.MAX_FUEL)
        elif kind == 'drs':
            if type(byte_count) is not int or byte_count < 0 or usage.drs_bytes + byte_count > permission.max_drs_bytes:
                raise ValueError('pure_drs_budget')
            usage = replace(usage, drs_bytes=usage.drs_bytes + byte_count)
        else:
            raise ValueError('pure_reservation_kind')
        host._pure_usage[permission.task_id] = usage
        host._revision += 1
        host._events.append(('PURE_NEED_RESERVED', host.state_revision, permission.task_id, kind, usage))
        return usage


def inspect_pure_need_resources_v01(host, *, task_id):
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        return host._pure_usage[task_id]


def _record_pure_drs_bytes_v01(host, task_id, byte_count):
    """Trusted local DRS completion accounting, never a resource refund."""
    with host._lock:
        usage=host._pure_usage[task_id]
        if type(byte_count) is not int or byte_count<0 or usage.measured_drs_bytes+byte_count>usage.drs_bytes:
            raise ValueError('pure_drs_observation_exceeds_reservation')
        host._pure_usage[task_id]=replace(usage,measured_drs_bytes=usage.measured_drs_bytes+byte_count)
        host._revision+=1
        host._events.append(('PURE_DRS_OBSERVED',host.state_revision,task_id,byte_count))


def install_admitted_pure_capability_v01(host, *, package, need, expected_revision):
    from dataclasses import asdict
    from hedgehog import capability_admission_v01 as pure
    from hedgehog.kernel import work_composition_v01 as work
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        if type(expected_revision) is not int or expected_revision != host.state_revision or host._active:
            raise ValueError('pure_stale_host_revision')
        work.validate_current_pure_need_v01(host, need=need)
        pure.validate_admitted_pure_package_v01(package, host=host, need=need)
        if not any(package is p for p in host._pure_pending) or any(r.need.need_id == need.need_id for r in host._pure_resolutions):
            raise ValueError('pure_install_not_pending_or_duplicate')
        admitted = package.native_admission
        if admitted.catalogue_revision != len(host._catalogue_history) or admitted.admission_id in host._catalogue:
            raise ValueError('pure_install_membership_epoch')
        host._refresh_admission(admitted, initial=True)
        resolution = pure.PureNeedResolutionV01('',need,package.package_id,admitted.definition.definition_id,
            admitted.admission_id,len(host._catalogue_history))
        material = asdict(resolution)
        del material['resolution_id']
        resolution = replace(resolution, resolution_id=pure.pure_evidence_identity_v01('pure_resolution',material))
        host._catalogue[admitted.admission_id] = admitted
        admitted._origin.owner = host
        host._pure_packages[admitted.admission_id] = package
        host._catalogue_history += (host.admitted_catalogue,)
        host._pure_resolutions += (resolution,)
        host._revision += 1
        host._events.append(('PURE_CATALOGUE_INSTALLED',host.state_revision,resolution))
        return resolution


def install_current_action_v01(host, *, root_bound, corridor, corridor_step,
    admission_id, inputs, transition_events, disposition_event, expected_revision,
    evaluation_time, evaluation_time_source, evaluation_context_id):
    """Install genuine Root authorization into this host's existing history.

    Setup supplies the public lifecycle evidence, never a replacement registry.
    All candidate validation finishes before publishing the registry/binding.
    """
    if type(host) is not RootWorkExecutionHostV01:
        raise ValueError('host_type')
    with host._lock:
        host._enter(expected_revision)
        try:
            host._refresh_sources(evaluation_time, evaluation_time_source, evaluation_context_id)
            view = action.common_action_view_v01(root_bound)
            canonical = view.canonical_projection
            if canonical.owning_local_root_id != host._root_id:
                raise ValueError('host_foreign_root')
            packet_id = view.packet_identity.packet_id
            if packet_id in host._bindings:
                raise ValueError('host_duplicate_packet_binding')
            admitted = host._catalogue[admission_id]
            host._refresh_admission(admitted)
            if firewall.snapshot_admitted_capability_v01(admitted) != canonical.execution_source:
                raise ValueError('host_packet_admission_mismatch')
            errors = firewall.validate_capability_business_binding_v01(admitted.definition, inputs, canonical)
            if errors:
                raise ValueError(errors[0])
            if type(transition_events) is not tuple or tuple(e.transition_rule_id for e in transition_events) != (
                'g2a_t01_activate_root_authorization', 'g2a_t02_queue', 'g2a_t03_pending'):
                raise ValueError('host_install_transition_sequence')
            profile = transitions.build_action_packet_transition_registry_profile_v01()
            proposed = action.record_action_packet_genesis_v01(host._registry,
                root_bound_genesis=root_bound, action_packet_transition_registry_profile=profile)
            proposed = action.activate_action_packet_lifecycle_v01(proposed, packet_id=packet_id,
                transition_event=transition_events[0], disposition_event=disposition_event,
                action_packet_transition_registry_profile=profile)
            for event in transition_events[1:]:
                proposed = action.append_action_packet_lifecycle_transition_v01(proposed,
                    packet_id=packet_id, transition_event=event, action_packet_transition_registry_profile=profile)
            inspection = action.inspect_action_packet_present_eligibility_v01(proposed, packet_id=packet_id,
                corridor=corridor, corridor_step=corridor_step,
                current_dependency_observations=host._packet_observations(canonical), logical_time_bridge=host._bridge,
                evaluation_time=evaluation_time, evaluation_time_source=evaluation_time_source,
                evaluation_context_id=evaluation_context_id, action_packet_transition_registry_profile=profile)
            if not inspection.present_executable:
                raise ValueError('host_installed_action_not_current')
            host._registry = proposed
            host._bindings[packet_id] = (corridor, corridor_step, admission_id, inputs)
            host._revision += 1
            host._events.append(('ROOT_ACTION_INSTALLED', host._revision, packet_id,
                view.root_decision_projection.root_decision_result.decision_id))
            return packet_id, host._revision
        finally:
            host._active = False
