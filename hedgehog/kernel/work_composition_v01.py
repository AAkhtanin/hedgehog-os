"""Finite typed work composition. Proposals carry data, never action authority.

The caller supplies validated semantic context and independently owned hosts.
Capability code computes values; public Root review authorizes concrete effects.
"""
from dataclasses import dataclass, fields, replace
import json
from pathlib import Path
import jsonschema
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog import capability_admission_v01 as pure
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import execution_mode_router_v01 as router
from hedgehog.kernel import fractal_runtime_v02 as fractal
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


@dataclass(frozen=True)
class WorkLiteralV01:
    value: action.ActionEffectParameterRecordV01


@dataclass(frozen=True)
class WorkOutputBindingV01:
    predecessor_work_id: str
    output_field: str
    expected_type: str


@dataclass(frozen=True)
class WorkHistoricalOutputV01:
    task_id: str
    revision_id: str
    predecessor_work_id: str
    invocation_id: str
    result_id: str
    admission_id: str
    result_artifact_ref: str
    output_field: str
    expected_type: str
    value: action.ActionEffectParameterRecordV01


@dataclass(frozen=True)
class WorkRevisionTriggerV01:
    trigger_id: str
    output: WorkHistoricalOutputV01


@dataclass(frozen=True)
class WorkContinuationContextV01:
    host: hosts.RootWorkExecutionHostV01
    snapshot: hosts.WorkTaskSnapshotV01
    trigger: WorkRevisionTriggerV01 | pure.PureMissingNeedTriggerV01 | None = None


@dataclass(frozen=True)
class WorkInputBindingV01:
    input_field: str
    source: WorkLiteralV01 | WorkOutputBindingV01 | WorkHistoricalOutputV01


@dataclass(frozen=True)
class WorkBudgetV01:
    max_items: int
    max_children: int
    max_model_calls: int
    max_compute_units: int
    max_revisions: int


@dataclass(frozen=True)
class WorkItemV01:
    work_id: str
    definition_id: str
    owning_root_id: str
    inputs: tuple[WorkInputBindingV01, ...]
    resource_refs: tuple[str, ...]
    depends_on: tuple[str, ...]
    guard: WorkOutputBindingV01 | None
    review_obligation_id: str | None


@dataclass(frozen=True)
class WorkProgramCandidateV01:
    task_id: str
    revision_id: str
    previous_revision_id: str | None
    intent_ref: str
    bsep_ref: str
    semantic_proposal_ref: str
    catalogue_revision: int
    budget: WorkBudgetV01
    items: tuple[WorkItemV01, ...]
    trigger_evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class MaterializedWorkProgramV01:
    candidate: WorkProgramCandidateV01
    topology_artifact: abi.KernelArtifactV01
    ordered_work_ids: tuple[str, ...]
    source_bindings: tuple[abi.CausalConsumptionRefV01, ...]


@dataclass(frozen=True)
class WorkItemResultV01:
    task_id: str
    revision_id: str
    work_id: str
    status: str
    invocation: firewall.BoundCapabilityInvocationV01 | None
    result: firewall.CapabilityExecutionResultV01 | None
    consumed_fields: tuple[abi.CausalConsumptionRefV01, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class WorkReviewObligationV01:
    obligation_id: str
    task_id: str
    revision_id: str
    work_id: str
    owning_root_id: str
    business_request_ref: str
    bsep_ref: str
    semantic_proposal_ref: str
    source_context: router.ExecutionModeSourceContextV01
    router_input: router.ExecutionModeRouterInputV01
    route_eligibility_artifact: abi.KernelArtifactV01
    root_route_review: router.RootExecutionModeDecisionV01


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


def _text(value):
    return type(value) is str and action.validate_identity_text_v01(value)[0]


def _plain(value):
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is tuple:
        return [_plain(v) for v in value]
    if type(value) is abi.KernelArtifactV01:
        return abi.kernel_artifact_to_plain_dict_v01(value)
    _require(type(value) in (WorkLiteralV01, WorkOutputBindingV01, WorkHistoricalOutputV01, WorkRevisionTriggerV01, WorkInputBindingV01,
        WorkBudgetV01, WorkItemV01, WorkProgramCandidateV01, WorkItemResultV01,
        hosts.WorkTaskPolicyV01, hosts.WorkTaskUsageV01, hosts.WorkTaskSnapshotV01, WorkTaskPendingActionV01,
        abi.CausalConsumptionRefV01, firewall.BoundCapabilityInvocationV01,
        firewall.CapabilityExecutionResultV01, firewall.CapabilityValidationEvidenceV01,
        action.ActionEffectParameterRecordV01), 'work_plain_type')
    return {f.name: _plain(getattr(value, f.name)) for f in fields(value)}


def _identity(leaf, value):
    return action.build_domain_separated_identity_v01(domain='hedgehog.common_action.' + leaf + '.v01',
        prefix=leaf + ':', material=(('payload', json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)),))


def _revision(candidate):
    value = _plain(candidate)
    del value['revision_id']
    return _identity('work_revision', value)


def _payload(value, kind):
    schema = json.loads((Path(__file__).resolve().parents[2] / 'schemas/work_composition_v01.schema.json').read_text())
    schema['$ref'] = '#/$defs/' + kind
    jsonschema.Draft202012Validator(schema).validate(value)
    return value


def _catalogue(catalogue):
    _require(type(catalogue) is tuple, 'work_catalogue_type')
    out = {}
    for admitted in catalogue:
        snapshot = firewall.snapshot_admitted_capability_v01(admitted)
        _require(snapshot.definition.definition_id not in out, 'work_duplicate_definition')
        out[snapshot.definition.definition_id] = admitted
    return out


def _order(items):
    remaining = {i.work_id: set(i.depends_on) for i in items}
    done = []
    while remaining:
        ready = sorted(k for k, parents in remaining.items() if parents <= set(done))
        _require(bool(ready), 'work_cycle')
        node = ready[0]
        done.append(node)
        del remaining[node]
    return tuple(done)


def _context(candidate, source_context, semantic_proposal):
    _require(type(source_context) is router.ExecutionModeSourceContextV01, 'work_context_type')
    _require(type(semantic_proposal) is abi.KernelArtifactV01 and not abi.validate_kernel_artifact_v01(semantic_proposal), 'work_semantic_artifact')
    _require((semantic_proposal.artifact_type, semantic_proposal.authority_class, semantic_proposal.lifecycle_state) ==
        ('SemanticArchitectProposal', 'ADVISORY', 'PROPOSED'), 'work_semantic_authority')
    _require(candidate.semantic_proposal_ref == semantic_proposal.artifact_id and
        candidate.bsep_ref == source_context.bsep_packet['packet_id'] and
        candidate.intent_ref in semantic_proposal.trace_refs and candidate.bsep_ref in semantic_proposal.parent_refs,
        'work_semantic_binding')
    router.build_execution_mode_bsep_binding_v01(request_id=candidate.task_id,
        transaction_id=semantic_proposal.transaction_id, owning_root_id=semantic_proposal.owner_root_id,
        domain_id=source_context.business_request_context_packet['domain'], source_context=source_context)


def validate_work_program_candidate_v01(candidate, *, catalogue, source_context, semantic_proposal, continuation_context=None):
    try:
        _require(type(candidate) is WorkProgramCandidateV01, 'work_candidate_type')
        _require(all(_text(getattr(candidate, n)) for n in ('task_id', 'revision_id', 'intent_ref', 'bsep_ref', 'semantic_proposal_ref')), 'work_identity')
        if continuation_context is None:
            _require(candidate.previous_revision_id is None, 'work_continuation_context_required')
        else:
            _validate_continuation_candidate(candidate, continuation_context, catalogue, source_context, semantic_proposal)
        _require(type(candidate.catalogue_revision) is int and candidate.catalogue_revision >= 0, 'work_catalogue_revision')
        budget = candidate.budget
        _require(type(budget) is WorkBudgetV01 and all(type(getattr(budget, f.name)) is int and
            0 <= getattr(budget, f.name) <= 4096 for f in fields(budget)), 'work_budget_type')
        _require(type(candidate.items) is tuple and 0 < len(candidate.items) <= budget.max_items <= 256 and
            len(candidate.items) <= budget.max_compute_units and budget.max_model_calls == 0, 'work_budget_exhausted')
        _require(type(candidate.trigger_evidence_refs) is tuple and all(_text(r) for r in candidate.trigger_evidence_refs)
            and len(set(candidate.trigger_evidence_refs)) == len(candidate.trigger_evidence_refs), 'work_trigger_refs')
        definitions = _catalogue(catalogue)
        if continuation_context is not None and continuation_context.host._pure_permissions:
            _validate_task_catalogue(candidate, continuation_context.host, catalogue)
        else:
            _require(all(a.catalogue_revision == candidate.catalogue_revision for a in catalogue), 'work_catalogue_revision')
        _require(all(type(i) is WorkItemV01 for i in candidate.items), 'work_item_type')
        items = {i.work_id: i for i in candidate.items}
        _require(len(items) == len(candidate.items), 'work_duplicate_id')
        for item in candidate.items:
            _require(all(_text(getattr(item, n)) for n in ('work_id', 'definition_id', 'owning_root_id')), 'work_item_identity')
            _require(type(item.inputs) is tuple and all(type(b) is WorkInputBindingV01 for b in item.inputs), 'work_inputs_type')
            _require(type(item.depends_on) is tuple and len(set(item.depends_on)) == len(item.depends_on) and
                all(p in items and p != item.work_id for p in item.depends_on), 'work_unknown_edge')
            _require(type(item.resource_refs) is tuple and all(_text(r) for r in item.resource_refs) and
                tuple(sorted(set(item.resource_refs))) == item.resource_refs, 'work_resource_scope')
            _require(item.review_obligation_id is None or _text(item.review_obligation_id), 'work_review_id')
            bindings = list(item.inputs)
            if item.guard is not None:
                _require(type(item.guard) is WorkOutputBindingV01 and item.guard.expected_type == 'BOOLEAN', 'work_guard_type')
                bindings.append(WorkInputBindingV01('guard', item.guard))
            for binding in bindings:
                _require(_text(binding.input_field), 'work_input_name')
                source = binding.source
                if type(source) is WorkLiteralV01:
                    _require(action.validate_action_effect_parameter_record_v01(source.value)[0], 'work_literal_value')
                    _require(source.value.parameter_name == binding.input_field, 'work_literal_name')
                else:
                    if type(source) is WorkHistoricalOutputV01:
                        _require(continuation_context is not None, 'work_historical_context_required')
                        _require(source.task_id == candidate.task_id, 'work_historical_foreign_task')
                        _historical_value(continuation_context.host, source, item, definitions)
                        continue
                    _require(type(source) is WorkOutputBindingV01, 'work_binding_type')
                    _require(source.predecessor_work_id in item.depends_on, 'work_undeclared_input_edge')
                    _require(_text(source.output_field) and _text(source.expected_type), 'work_output_binding')
                    producer = items[source.predecessor_work_id]
                    _require(producer.owning_root_id == item.owning_root_id, 'work_foreign_root_input')
                    if producer.definition_id in definitions:
                        fields_by_name = {f.name: f for f in definitions[producer.definition_id].definition.output_fields}
                        _require(source.output_field in fields_by_name and fields_by_name[source.output_field].value_type == source.expected_type,
                            'work_output_contract')
            if item.definition_id in definitions:
                definition = definitions[item.definition_id].definition
                _require(item.resource_refs == definition.resource_refs, 'work_resource_scope')
                declared = {f.name: f for f in definition.input_fields}
                names = tuple(b.input_field for b in item.inputs)
                _require(len(set(names)) == len(names) and set(names) <= set(declared) and
                    {f.name for f in definition.input_fields if f.required} <= set(names), 'work_input_contract')
                for binding in item.inputs:
                    actual_type = binding.source.value.value_type if type(binding.source) is WorkLiteralV01 else binding.source.expected_type
                    _require(actual_type == declared[binding.input_field].value_type, 'work_input_contract_type')
        _order(candidate.items)
        _context(candidate, source_context, semantic_proposal)
        _require(candidate.revision_id == _revision(candidate), 'work_revision_identity')
        _payload(_plain(candidate), 'program')
        return True, ()
    except (ValueError, TypeError, KeyError, AttributeError, jsonschema.ValidationError) as exc:
        return False, (str(exc) if type(exc) is ValueError else 'work_candidate_shape',)


def build_work_program_candidate_v01(*, task_id, previous_revision_id, intent_ref, bsep_ref,
    semantic_proposal_ref, catalogue_revision, budget, items, trigger_evidence_refs,
    catalogue, source_context, semantic_proposal, continuation_context=None):
    candidate = WorkProgramCandidateV01(task_id, '', previous_revision_id, intent_ref, bsep_ref,
        semantic_proposal_ref, catalogue_revision, budget, items, trigger_evidence_refs)
    candidate = replace(candidate, revision_id=_revision(candidate))
    ok, reasons = validate_work_program_candidate_v01(candidate, catalogue=catalogue,
        source_context=source_context, semantic_proposal=semantic_proposal, continuation_context=continuation_context)
    _require(ok, reasons[0] if reasons else 'work_invalid')
    return candidate


def work_program_candidate_to_artifact_v01(candidate, *, catalogue, source_context, semantic_proposal, continuation_context=None):
    ok, reasons = validate_work_program_candidate_v01(candidate, catalogue=catalogue,
        source_context=source_context, semantic_proposal=semantic_proposal, continuation_context=continuation_context)
    _require(ok, reasons[0] if reasons else 'work_invalid')
    payload = _payload({'work_program': _plain(candidate)}, 'proposal_payload')
    return abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id=_identity('work_proposal', payload),
        artifact_type='SemanticArchitectProposal', schema_version='v1', transaction_id=semantic_proposal.transaction_id,
        owner_root_id=semantic_proposal.owner_root_id, source_component='semantic_architect', authority_class='ADVISORY',
        lifecycle_state='PROPOSED', payload=payload, trace_refs=(candidate.task_id, candidate.revision_id),
        parent_refs=(semantic_proposal.artifact_id,),
        time_envelope=abi.kernel_artifact_to_plain_dict_v01(semantic_proposal)['time_envelope'])


def materialize_work_program_v01(candidate, *, catalogue, source_context, semantic_proposal, continuation_context=None):
    proposal = work_program_candidate_to_artifact_v01(candidate, catalogue=catalogue,
        source_context=source_context, semantic_proposal=semantic_proposal, continuation_context=continuation_context)
    ordered = _order(candidate.items)
    payload = _payload({'work_program': _plain(candidate), 'ordered_work_ids': list(ordered)}, 'topology_payload')
    source = abi.kernel_artifact_to_plain_dict_v01(semantic_proposal)
    topology = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id=_identity('work_topology', payload),
        artifact_type='RuntimeExecutionTopology', schema_version='v1', transaction_id=semantic_proposal.transaction_id,
        owner_root_id=semantic_proposal.owner_root_id, source_component='runtime', authority_class='NON_AUTHORITY',
        lifecycle_state='VALIDATED', payload=payload, trace_refs=(candidate.task_id, candidate.revision_id),
        parent_refs=(proposal.artifact_id,), time_envelope=source['time_envelope'])
    bindings = tuple(abi.build_causal_consumption_ref_v01(producer_actor_id='semantic_architect',
        source_artifact_id=proposal.artifact_id, output_field='/work_program/' + field,
        consumer_component='work_composition', downstream_artifact_id=topology.artifact_id,
        decision_effect='materialize_work', disposition='USED', reason_code='used:validated_program_' + field,
        trace_refs=(candidate.task_id, candidate.revision_id)) for field in ('items', 'budget', 'bsep_ref'))
    return MaterializedWorkProgramV01(candidate, topology, ordered, bindings)


def _work_ref(candidate, item):
    return _identity('work_instance', [candidate.task_id, candidate.revision_id, item.work_id])


def _consume(candidate, item, binding, prior, definitions, host_map):
    if type(binding) is WorkHistoricalOutputV01:
        _require(binding.task_id == candidate.task_id, 'work_historical_foreign_task')
        host = host_map[item.owning_root_id]
        value = _historical_value(host, binding, item, definitions)
        ref = abi.build_causal_consumption_ref_v01(producer_actor_id=binding.predecessor_work_id,
            source_artifact_id=binding.result_id, output_field='/' + binding.output_field.replace('~', '~0').replace('/', '~1'),
            consumer_component='work_composition', downstream_artifact_id=_work_ref(candidate, item),
            decision_effect='bind_input', disposition='USED', reason_code='used:actual_historical_output_field',
            trace_refs=(candidate.task_id, candidate.revision_id, binding.revision_id, binding.invocation_id, binding.result_artifact_ref))
        return value, ref
    producer = next(i for i in candidate.items if i.work_id == binding.predecessor_work_id)
    _require(producer.work_id in prior, 'work_missing_producer')
    previous = prior[producer.work_id]
    _require(previous.status == 'COMPLETED', 'work_producer_not_completed')
    _validate_completed(candidate, producer, previous, definitions, host_map)
    outputs = {v.parameter_name: v for v in previous.result.output}
    _require(binding.output_field in outputs, 'work_missing_output_field')
    value = outputs[binding.output_field]
    _require(value.value_type == binding.expected_type, 'work_output_type')
    ref = abi.build_causal_consumption_ref_v01(producer_actor_id=producer.work_id,
        source_artifact_id=previous.result.result_id, output_field='/' + binding.output_field.replace('~', '~0').replace('/', '~1'),
        consumer_component='work_composition', downstream_artifact_id=_work_ref(candidate, item),
        decision_effect='bind_input', disposition='USED', reason_code='used:actual_output_field',
        trace_refs=(candidate.task_id, candidate.revision_id, previous.invocation.invocation_id, item.work_id))
    return value, ref


def _validate_completed(candidate, item, value, definitions, host_map):
    _require(type(value) is WorkItemResultV01 and
        (value.task_id, value.revision_id, value.work_id) == (candidate.task_id, candidate.revision_id, item.work_id), 'work_result_context')
    _require(value.status == 'COMPLETED' and value.reasons == (), 'work_result_not_complete')
    admitted = definitions[item.definition_id]
    snapshot = firewall.snapshot_admitted_capability_v01(admitted)
    _require(not firewall.validate_capability_execution_result_v01(value.result, value.invocation, snapshot), 'work_result_validation')
    _require(value.result.outcome == 'SUCCEEDED' and value.invocation.owning_root_id == item.owning_root_id and
        value.invocation.task_id == candidate.task_id, 'work_result_root_task')
    host = host_map[item.owning_root_id]
    _require(type(host) is hosts.RootWorkExecutionHostV01 and host.owning_root_id == item.owning_root_id and
        any((value.invocation, value.result) == pair for pair in host.completed_work), 'work_result_not_observed')
    _require(value.invocation.work_instance_id == _work_ref(candidate, item), 'work_result_instance')


def _inputs(candidate, item, prior, definitions, host_map):
    values, refs = [], []
    for binding in item.inputs:
        if type(binding.source) is WorkLiteralV01:
            value = binding.source.value
        else:
            value, ref = _consume(candidate, item, binding.source, prior, definitions, host_map)
            refs.append(ref)
        values.append(action.build_action_effect_parameter_record_v01(parameter_name=binding.input_field,
            value_type=value.value_type, value=value.value))
    return tuple(sorted(values, key=lambda v: v.parameter_name)), tuple(refs)


def _reviews(bindings):
    _require(type(bindings) is tuple and all(type(b) is tuple and len(b) == 3 and
        type(b[0]) is WorkReviewObligationV01 for b in bindings), 'work_review_bindings_shape')
    result = {o.obligation_id: (o, s, b) for o, s, b in bindings}
    _require(len(result) == len(bindings), 'work_duplicate_review')
    return result


def _review(candidate, item, reviews, semantic_proposal):
    if item.review_obligation_id is not None:
        _require(item.review_obligation_id in reviews, 'work_required_review_missing')
        obligation, source, bundle = reviews[item.review_obligation_id]
        ok, reasons = validate_work_review_binding_v01(obligation, candidate=candidate, item=item,
            source_context=source, execution_bundle=bundle, semantic_proposal=semantic_proposal)
        _require(ok, reasons[0] if reasons else 'work_review_invalid')


def _readiness(candidate, item, prior, definitions, host_map, reviews, semantic_proposal):
    if item.definition_id not in definitions:
        return 'NEEDS_CAPABILITY', 'work_unknown_capability', (), ()
    if any(p not in prior or prior[p].status not in ('COMPLETED', 'SKIPPED_GUARD_FALSE') for p in item.depends_on):
        return 'BLOCKED_REQUIRED_OUTPUT', 'work_required_parent', (), ()
    try:
        host = host_map[item.owning_root_id]
        _require(type(host) is hosts.RootWorkExecutionHostV01 and host.owning_root_id == item.owning_root_id, 'work_host_root')
        _require(any(definitions[item.definition_id] is a for a in host.admitted_catalogue), 'work_host_admission')
        values, refs = _inputs(candidate, item, prior, definitions, host_map)
        if item.guard is not None:
            guard, ref = _consume(candidate, item, item.guard, prior, definitions, host_map)
            _require(guard.value_type == 'BOOLEAN' and type(guard.value) is bool, 'work_guard_type')
            if guard.value is False:
                return 'SKIPPED_GUARD_FALSE', 'work_guard_false', (), (ref,)
            refs += (ref,)
        _review(candidate, item, reviews, semantic_proposal)
        return 'READY', 'work_root_action_required', values, refs
    except (ValueError, KeyError) as exc:
        return 'BLOCKED_INVALID_INPUT', str(exc) if type(exc) is ValueError else 'work_binding_missing', (), ()


def _attempts(candidate, item, host_map):
    host = host_map.get(item.owning_root_id)
    if type(host) is not hosts.RootWorkExecutionHostV01:
        return ()
    return tuple(a for a in host.work_attempts if a.task_id == candidate.task_id and
        a.work_instance_id == _work_ref(candidate, item))


def validate_work_program_result_v01(program, results, *, catalogue, host_map,
    source_context, semantic_proposal, review_bindings=(), continuation_context=None):
    try:
        _require(type(program) is MaterializedWorkProgramV01 and type(results) is tuple, 'work_results_type')
        candidate = program.candidate
        _require(program == materialize_work_program_v01(candidate, catalogue=catalogue,
            source_context=source_context, semantic_proposal=semantic_proposal, continuation_context=continuation_context), 'work_materialization_binding')
        reviews = _reviews(review_bindings)
        _require(all(s.g2c_source_context == source_context and o.router_input.transaction_id ==
            semantic_proposal.transaction_id for o, s, _ in reviews.values()), 'work_review_program_context')
        definitions = _catalogue(catalogue)
        items = {i.work_id: i for i in candidate.items}
        previous = {}
        positions = []
        for value in results:
            _require(type(value) is WorkItemResultV01 and value.work_id in items and value.work_id not in previous, 'work_result_key')
            item = items[value.work_id]
            _require((value.task_id, value.revision_id) == (candidate.task_id, candidate.revision_id), 'work_result_context')
            _require(type(value.consumed_fields) is tuple and all(not abi.validate_causal_consumption_ref_v01(r)
                for r in value.consumed_fields), 'work_consumption_shape')
            if value.status == 'COMPLETED':
                _review(candidate, item, reviews, semantic_proposal)
                _validate_completed(candidate, item, value, definitions, host_map)
                _require(all(p in previous and previous[p].status in ('COMPLETED', 'SKIPPED_GUARD_FALSE') for p in item.depends_on), 'work_required_parent')
                inputs, refs = _inputs(candidate, item, previous, definitions, host_map)
                if item.guard is not None:
                    guard, ref = _consume(candidate, item, item.guard, previous, definitions, host_map)
                    _require(guard.value_type == 'BOOLEAN' and guard.value is True, 'work_guard_not_true')
                    refs += (ref,)
                _require(inputs == value.invocation.inputs and refs == value.consumed_fields, 'work_consumed_input_binding')
            elif value.status in ('FAILED_NON_CONSUMING', 'UNCERTAIN_CLOSED'):
                attempts = _attempts(candidate, item, host_map)
                _require(len(attempts) == 1, 'work_attempt_not_observed')
                actual = attempts[0]
                inputs, refs = _inputs(candidate, item, previous, definitions, host_map)
                if item.guard is not None:
                    guard, ref = _consume(candidate, item, item.guard, previous, definitions, host_map)
                    _require(guard.value is True, 'work_guard_not_true')
                    refs += (ref,)
                _require((value.status, value.invocation, value.result, value.reasons, value.consumed_fields) ==
                    (actual.disposition, actual.invocation, actual.result, (actual.reason,), refs) and
                    actual.inputs == inputs and actual.admission_id == definitions[item.definition_id].admission_id,
                    'work_attempt_binding')
            else:
                status, reason, _, refs = _readiness(candidate, item, previous, definitions, host_map, reviews, semantic_proposal)
                _require((value.status, value.reasons, value.consumed_fields, value.invocation, value.result) ==
                    (status, (reason,), refs, None, None), 'work_noncompletion_cause')
                _require(not _attempts(candidate, item, host_map), 'work_attempt_history_omitted')
                if status == 'READY':
                    _require(definitions[item.definition_id].definition.effect_kind != 'PURE', 'work_pure_not_dispatched')
            previous[value.work_id] = value
            positions.append(program.ordered_work_ids.index(value.work_id))
        _require(positions == sorted(positions), 'work_result_order')
        _payload({'topology_ref': program.topology_artifact.artifact_id,
            'work_results': [_plain(r) for r in results]}, 'result_payload')
        return True, ()
    except (ValueError, TypeError, KeyError, AttributeError, StopIteration, jsonschema.ValidationError) as exc:
        return False, (str(exc) if type(exc) is ValueError else 'work_result_shape',)


def _advance_work_program_v01(program, *, catalogue, source_context, semantic_proposal,
    host_map, results=(), review_bindings=(), action_authorizers=None, continuation_context=None):
    """Reduce supplied completed work, then dispatch at most the finite remainder.

    An authorizer receives resolved actual inputs. Its return is a public Root
    packet and lifecycle evidence for install_current_action_v01, not a bool.
    """
    _require(type(program) is MaterializedWorkProgramV01, 'work_program_type')
    expected = materialize_work_program_v01(program.candidate, catalogue=catalogue,
        source_context=source_context, semantic_proposal=semantic_proposal, continuation_context=continuation_context)
    _require(program == expected, 'work_materialization_binding')
    candidate = program.candidate
    definitions = _catalogue(catalogue)
    items = {i.work_id: i for i in candidate.items}
    _require(type(results) is tuple and all(type(r) is WorkItemResultV01 for r in results), 'work_prior_type')
    _require(len({r.work_id for r in results}) == len(results), 'work_prior_duplicate')
    _require(all(r.work_id in items and (r.task_id, r.revision_id) == (candidate.task_id, candidate.revision_id)
        for r in results), 'work_prior_context')
    # Deferred values confer no progress. Recompute their current cause; only
    # validated terminal history may suppress a dispatch in this finite pass.
    terminal = tuple(r for r in results if r.status in ('COMPLETED', 'FAILED_NON_CONSUMING', 'UNCERTAIN_CLOSED', 'SKIPPED_GUARD_FALSE'))
    ok, reasons = validate_work_program_result_v01(program, terminal, catalogue=catalogue, host_map=host_map,
        source_context=source_context, semantic_proposal=semantic_proposal, review_bindings=review_bindings, continuation_context=continuation_context)
    _require(ok, reasons[0] if reasons else 'work_prior_invalid')
    prior = {r.work_id: r for r in terminal}
    authorizers = {} if action_authorizers is None else action_authorizers
    reviews = _reviews(review_bindings)
    for work_id in program.ordered_work_ids:
        if work_id in prior:
            continue
        item = items[work_id]
        _require(not _attempts(candidate, item, host_map), 'work_attempt_history_omitted')
        status, reason, values, refs = _readiness(candidate, item, prior, definitions, host_map, reviews, semantic_proposal)
        invocation = result = None
        if status == 'READY':
            host = host_map[item.owning_root_id]
            admitted = definitions[item.definition_id]
            attempts = sum(len(_attempts(candidate, i, host_map)) for i in candidate.items)
            _require(attempts < candidate.budget.max_compute_units, 'work_attempt_budget_exhausted')
            if continuation_context is not None:
                host._task_dispatch = (candidate.task_id, _work_ref(candidate, item), admitted.admission_id, values)
            try:
                if admitted.definition.effect_kind == 'PURE':
                    invocation, result, _ = hosts.execute_admitted_pure_work_v01(host,
                        admission_id=admitted.admission_id, task_id=candidate.task_id,
                        work_instance_id=_work_ref(candidate, item), inputs=values, expected_revision=host.state_revision)
                elif item.owning_root_id not in authorizers and (continuation_context is None or
                    _pending_task_action(host, candidate, item) is None):
                    prior[work_id] = WorkItemResultV01(candidate.task_id, candidate.revision_id, work_id,
                        'READY', None, None, refs, ('work_root_action_required',))
                    continue
                else:
                    clock = host.current_sources
                    pending = None if continuation_context is None else _pending_task_action(host, candidate, item)
                    if pending is None:
                        authorization = authorizers[item.owning_root_id](candidate, item, values, admitted)
                        _require(type(authorization) is dict and set(authorization) == {'root_bound', 'corridor', 'corridor_step',
                            'transition_events', 'disposition_event'}, 'work_root_authorization_shape')
                        view = action.common_action_view_v01(authorization['root_bound'])
                        _require(view.canonical_projection.transaction_id == program.topology_artifact.transaction_id,
                            'work_action_transaction')
                        clock = host.current_sources
                        packet_id, revision = hosts.install_current_action_v01(host, **authorization,
                            admission_id=admitted.admission_id, inputs=values, expected_revision=host.state_revision,
                            evaluation_time=clock.evaluation_time, evaluation_time_source=clock.evaluation_time_source,
                            evaluation_context_id=clock.evaluation_context_id)
                    else:
                        _require(pending.inputs == values and pending.admission_id == admitted.admission_id, 'work_task_pending_inputs')
                        packet_id, revision = pending.packet_id, host.state_revision
                    registry, _ = hosts.dispatch_current_action_v01(host, packet_id=packet_id,
                        task_id=candidate.task_id, expected_revision=revision, evaluation_time=clock.evaluation_time,
                        evaluation_time_source=clock.evaluation_time_source, evaluation_context_id=clock.evaluation_context_id,
                        work_instance_id=_work_ref(candidate, item))
                    context = registry.action_packet_fulfillment_attempt_contexts[-1]
                    _require(context.receipt is not None, 'work_effect_not_completed')
                    payload = abi.kernel_artifact_to_plain_dict_v01(context.receipt)['payload']
                    evidence = firewall.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])
                    invocation, result = evidence.invocation, evidence.result
                observed = _attempts(candidate, item, host_map)
                _require(len(observed) == 1, 'work_attempt_not_observed')
                status, reason = observed[0].disposition, observed[0].reason
            except Exception as exc:
                observed = _attempts(candidate, item, host_map)
                if isinstance(exc, _TaskExhausted):
                    if len(observed) == 1:
                        actual = observed[0]
                        _retain_task_result(host, program, WorkItemResultV01(candidate.task_id, candidate.revision_id,
                            work_id, actual.disposition, actual.invocation, actual.result, refs, (actual.reason,)))
                    raise
                if len(observed) != 1:
                    raise
                status, reason = observed[0].disposition, observed[0].reason
                invocation, result = observed[0].invocation, observed[0].result
        prior[work_id] = WorkItemResultV01(candidate.task_id, candidate.revision_id, work_id,
            status, invocation, result, refs, () if reason is None else (reason,))
        if continuation_context is not None:
            _retain_task_result(continuation_context.host, program, prior[work_id])
    output = tuple(prior[w] for w in program.ordered_work_ids)
    ok, reasons = validate_work_program_result_v01(program, output, catalogue=catalogue, host_map=host_map,
        source_context=source_context, semantic_proposal=semantic_proposal, review_bindings=review_bindings, continuation_context=continuation_context)
    _require(ok, reasons[0] if reasons else 'work_result_invalid')
    return output


def work_program_result_to_artifact_v01(program, results, *, catalogue, host_map,
    source_context, semantic_proposal, review_bindings=(), continuation_context=None):
    ok, reasons = validate_work_program_result_v01(program, results, catalogue=catalogue, host_map=host_map,
        source_context=source_context, semantic_proposal=semantic_proposal, review_bindings=review_bindings, continuation_context=continuation_context)
    _require(ok, reasons[0] if reasons else 'work_result_invalid')
    payload = _payload({'topology_ref': program.topology_artifact.artifact_id,
        'work_results': [_plain(r) for r in results]}, 'result_payload')
    return abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id=_identity('work_results', payload),
        artifact_type='ResultProposal', schema_version='v1', transaction_id=program.topology_artifact.transaction_id,
        owner_root_id=program.topology_artifact.owner_root_id, source_component='work_composition',
        authority_class='EVIDENCE_ONLY', lifecycle_state='PROPOSED', payload=payload,
        trace_refs=(program.candidate.task_id, program.candidate.revision_id),
        parent_refs=(program.topology_artifact.artifact_id,),
        time_envelope=abi.kernel_artifact_to_plain_dict_v01(program.topology_artifact)['time_envelope'])


def work_review_commitment_to_plain_data_v01(*, candidate, item, source_context, semantic_proposal):
    """Upstream work and source preimage, excluding downstream review identities."""
    _require(type(candidate) is WorkProgramCandidateV01 and type(item) is WorkItemV01, 'work_review_candidate_type')
    _payload(_plain(candidate), 'program')
    _require((candidate.previous_revision_id is None or _text(candidate.previous_revision_id)) and candidate.revision_id == _revision(candidate), 'work_revision_identity')
    items = {i.work_id: i for i in candidate.items}
    _require(len(items) == len(candidate.items) and items.get(item.work_id) == item, 'work_review_member')
    _order(candidate.items)
    _context(candidate, source_context, semantic_proposal)
    pending, relevant = [item.work_id], set()
    while pending:
        key = pending.pop()
        _require(key in items, 'work_unknown_edge')
        if key not in relevant:
            relevant.add(key)
            pending.extend(items[key].depends_on)
    projection = []
    for key in sorted(relevant):
        value = _plain(items[key])
        del value['review_obligation_id']
        projection.append(value)
    material = dict(profile='work_control_scope.v01', task_id=candidate.task_id,
        intent_ref=candidate.intent_ref, bsep_ref=candidate.bsep_ref,
        semantic_proposal_ref=candidate.semantic_proposal_ref, catalogue_revision=candidate.catalogue_revision,
        budget=_plain(candidate.budget), trigger_evidence_refs=list(candidate.trigger_evidence_refs),
        reviewed_work_id=item.work_id, dependency_program=projection,
        business_source=source_context.business_request_context_packet,
        bsep_sources=dict(packet=source_context.bsep_packet, route=source_context.bsep_route_context_packet,
            proposal=source_context.bsep_orchestrator_proposal, rationale=source_context.bsep_structured_rationale),
        semantic_source=abi.kernel_artifact_to_plain_dict_v01(semantic_proposal))
    return json.loads(canonical_json_bytes_v01(material))


def build_work_review_scope_ref_v01(*, candidate, item, source_context, semantic_proposal):
    material = work_review_commitment_to_plain_data_v01(candidate=candidate, item=item,
        source_context=source_context, semantic_proposal=semantic_proposal)
    return action.build_domain_separated_identity_v01(domain='hedgehog.common_action.work_control_scope.v01',
        prefix='work_control_scope:', material=(('payload', canonical_json_bytes_v01(material).decode('utf-8')),))


def build_work_review_obligation_v01(*, candidate, item, source_context):
    _require(type(source_context) is fractal.FractalRuntimeSourceContextV02, 'work_review_source_type')
    value = WorkReviewObligationV01('', candidate.task_id, candidate.revision_id, item.work_id,
        item.owning_root_id, source_context.g2c_source_context.business_request_context_packet['packet_id'],
        candidate.bsep_ref, candidate.semantic_proposal_ref, source_context.g2c_source_context,
        source_context.router_input, source_context.route_eligibility_artifact, source_context.decision)
    return replace(value, obligation_id=_review_id(value))


def _review_id(value):
    # The candidate includes this obligation ID; its revision cannot be an ID
    # preimage too. Revision remains an independently checked contextual field.
    return _identity('work_review', [value.task_id, value.work_id, value.owning_root_id,
        value.business_request_ref, value.bsep_ref, value.semantic_proposal_ref,
        router.execution_mode_router_input_to_plain_data_v01(value.router_input),
        _plain(value.route_eligibility_artifact), router.root_execution_mode_decision_to_plain_data_v01(value.root_route_review)])


def validate_work_review_binding_v01(value, *, candidate, item, source_context, execution_bundle, semantic_proposal=None):
    try:
        _require(type(value) is WorkReviewObligationV01 and type(source_context) is fractal.FractalRuntimeSourceContextV02 and
            type(execution_bundle) is fractal.FractalRuntimeExecutionBundleV02, 'work_review_type')
        _require(value == build_work_review_obligation_v01(candidate=candidate, item=item, source_context=source_context) and
            value.obligation_id == item.review_obligation_id, 'work_review_identity')
        _require((value.task_id, value.revision_id, value.work_id, value.owning_root_id) ==
            (candidate.task_id, candidate.revision_id, item.work_id, item.owning_root_id), 'work_review_task')
        _require(value.bsep_ref == source_context.g2c_source_context.bsep_packet['packet_id'] and
            value.router_input.request_id == candidate.task_id and value.router_input.owning_root_id == item.owning_root_id,
            'work_review_source_context')
        _require(execution_bundle.source_context == source_context, 'work_review_bundle_source')
        _require(semantic_proposal is not None, 'work_review_semantic_source_required')
        scope = build_work_review_scope_ref_v01(candidate=candidate, item=item,
            source_context=source_context.g2c_source_context, semantic_proposal=semantic_proposal)
        _require(source_context.router_input.local_routing_snapshot.scope_ref == scope and
            source_context.proposal.proposed_scope_ref == scope and source_context.decision.accepted_scope_ref == scope and
            execution_bundle.source_binding.accepted_scope_ref == scope, 'work_review_exact_scope')
        checks = (fractal.validate_runtime_topology_source_binding_against_g2c_v02(execution_bundle.source_binding, source_context=source_context),
            fractal.validate_runtime_execution_topology_against_sources_v02(execution_bundle.topology, source_context=source_context),
            fractal.validate_fractal_runtime_execution_bundle_v02(execution_bundle))
        _require(all(r.status == 'PASS' for r in checks), 'work_review_public_validation')
        report = execution_bundle.runtime_report
        _require(report.runtime_outcome == 'COMPLETED' and report.blocked_cell_count == 0 and report.parent_return_refs and
            report.completed_cell_count == len(execution_bundle.cell_results) and
            any(t.decision_id == report.parent_return_transition_decision_id for t in execution_bundle.transition_decisions),
            'work_review_not_completed')
        _require(len(execution_bundle.cell_results) - 1 <= candidate.budget.max_children, 'work_review_child_budget')
        _payload(dict(obligation_id=value.obligation_id, task_id=value.task_id, revision_id=value.revision_id,
            work_id=value.work_id, owning_root_id=value.owning_root_id, business_request_ref=value.business_request_ref,
            bsep_ref=value.bsep_ref, semantic_proposal_ref=value.semantic_proposal_ref,
            router_input_ref=value.router_input.router_input_id, route_eligibility_ref=value.route_eligibility_artifact.artifact_id,
            root_route_review_ref=value.root_route_review.decision_id, runtime_report_ref=report.report_id,
            parent_return_refs=list(report.parent_return_refs)), 'review_payload')
        return True, ()
    except (ValueError, TypeError, AttributeError, KeyError, jsonschema.ValidationError) as exc:
        return False, (str(exc) if type(exc) is ValueError else 'work_review_shape',)


@dataclass(frozen=True)
class WorkContinuationOutcomeV01:
    program: MaterializedWorkProgramV01
    results: tuple[WorkItemResultV01, ...]
    snapshot: hosts.WorkTaskSnapshotV01
    status: str
    reason: str | None


@dataclass(frozen=True)
class _TaskRevision:
    program: MaterializedWorkProgramV01
    source_context: router.ExecutionModeSourceContextV01
    semantic_proposal: abi.KernelArtifactV01
    trigger: WorkRevisionTriggerV01 | None
    results: tuple[WorkItemResultV01, ...]
    artifact: abi.KernelArtifactV01 | None
    accepted_usage: hosts.WorkTaskUsageV01
    catalogue: tuple = ()


@dataclass(frozen=True)
class _TaskLedger:
    policy: hosts.WorkTaskPolicyV01
    usage: hosts.WorkTaskUsageV01
    revisions: tuple[_TaskRevision, ...]
    reviews: tuple[tuple[WorkReviewObligationV01, fractal.FractalRuntimeSourceContextV02, fractal.FractalRuntimeExecutionBundleV02], ...]
    charged_instances: tuple[str, ...]
    pending_actions: 'tuple[WorkTaskPendingActionV01, ...]'
    outcome: str
    reason: str | None


class _TaskExhausted(ValueError):
    pass


@dataclass(frozen=True)
class WorkTaskPendingActionV01:
    revision_id: str
    work_id: str
    packet_id: str
    admission_id: str
    inputs: tuple[action.ActionEffectParameterRecordV01, ...]


def _pending_task_action(host, candidate, item):
    return next((p for p in _ledger(host, candidate.task_id).pending_actions
        if (p.revision_id, p.work_id) == (candidate.revision_id, item.work_id)), None)


def prepare_work_task_action_v01(context, *, work_id, authorization, catalogue,
    source_context, semantic_proposal, review_bindings=()):
    """Retain current Root authorization without starting its pending effect."""
    _require(type(context) is WorkContinuationContextV01, 'work_task_context_type')
    host = context.host
    with host._lock:
        ledger = _current_context(context)
        _require(ledger.outcome != 'EXHAUSTED', 'work_task_exhausted')
        current = ledger.revisions[-1]
        candidate = current.program.candidate
        _policy_candidate(ledger.policy, candidate, source_context, semantic_proposal)
        item = next((i for i in candidate.items if i.work_id == work_id), None)
        _require(item is not None, 'work_task_pending_item')
        _require(_pending_task_action(host, candidate, item) is None, 'work_task_pending_duplicate')
        prior = {r.work_id: r for r in current.results}
        definitions = _catalogue(catalogue)
        status, _, inputs, _ = _readiness(candidate, item, prior, definitions, {host.owning_root_id: host},
            _reviews(review_bindings), semantic_proposal)
        _require(status == 'READY' and definitions[item.definition_id].definition.effect_kind != 'PURE', 'work_task_pending_not_ready')
        _require(type(authorization) is dict and set(authorization) == {'root_bound', 'corridor', 'corridor_step',
            'transition_events', 'disposition_event'}, 'work_root_authorization_shape')
        _require(action.common_action_view_v01(authorization['root_bound']).canonical_projection.transaction_id ==
            current.program.topology_artifact.transaction_id, 'work_action_transaction')
        admitted = definitions[item.definition_id]
        clock = host.current_sources
        packet_id, _ = hosts.install_current_action_v01(host, **authorization, admission_id=admitted.admission_id,
            inputs=inputs, expected_revision=host.state_revision, evaluation_time=clock.evaluation_time,
            evaluation_time_source=clock.evaluation_time_source, evaluation_context_id=clock.evaluation_context_id)
        pending = WorkTaskPendingActionV01(candidate.revision_id, item.work_id, packet_id, admitted.admission_id, inputs)
        _payload(_plain(pending), 'pending_action')
        host._tasks[candidate.task_id] = replace(_ledger(host, candidate.task_id), pending_actions=(*ledger.pending_actions, pending))
        return pending


def _source_ref(source_context, semantic_proposal):
    from collections.abc import Mapping
    from dataclasses import is_dataclass

    def plain(value):
        if value is None or type(value) in (str, int, bool, float):
            return value
        if isinstance(value, Mapping):
            return {k: plain(v) for k, v in value.items()}
        if type(value) in (tuple, list):
            return [plain(v) for v in value]
        _require(is_dataclass(value), 'work_task_source_shape')
        return {f.name: plain(getattr(value, f.name)) for f in fields(value)}

    material = plain(source_context)
    # Without a G2-A packet these are downstream routing-observation coordinates,
    # not original business/BSEP authority. Actual review validates its own view.
    if source_context.g2a_registry is None:
        for name in ('g2a_evaluation_time', 'g2a_evaluation_time_source', 'g2a_evaluation_context_id'):
            material.pop(name, None)
    return _identity('work_task_source', [material, _plain(semantic_proposal)])


def validate_installed_work_task_policy_v01(policy, *, owning_root_id, catalogue):
    """Validate trusted configuration; this does not grant Root action authority."""
    _require(type(policy) is hosts.WorkTaskPolicyV01, 'work_task_policy_type')
    _require(all(_text(getattr(policy, f)) for f in ('task_id', 'owning_root_id', 'host_instance_ref',
        'initial_revision_id', 'intent_ref', 'source_ref')), 'work_task_policy_identity')
    _require(policy.owning_root_id == owning_root_id, 'work_task_policy_root')
    _require(all(type(getattr(policy, f)) is int and 0 <= getattr(policy, f) <= 4096
        for f in ('max_items', 'max_compute_units', 'max_children', 'max_model_calls', 'max_revisions')),
        'work_task_policy_budget')
    _require(0 < policy.max_items <= 256 and policy.max_compute_units > 0 and
        policy.max_model_calls == 0 and policy.max_revisions <= 2, 'work_task_policy_profile')
    for values in (policy.definition_ids, policy.review_definition_ids, policy.resource_refs):
        _require(type(values) is tuple and all(_text(v) for v in values) and values == tuple(sorted(set(values))), 'work_task_policy_scope')
    _require(set(policy.review_definition_ids) <= set(policy.definition_ids), 'work_task_policy_review_scope')
    for admitted in _catalogue(catalogue).values():
        _require(admitted.host_instance_ref == policy.host_instance_ref, 'work_task_policy_host')
    _payload(_plain(policy), 'task_policy')
    return True


def build_work_task_policy_v01(candidate, *, catalogue, source_context, semantic_proposal,
    host_instance_ref, definition_ids, resource_refs):
    ok, reasons = validate_work_program_candidate_v01(candidate, catalogue=catalogue,
        source_context=source_context, semantic_proposal=semantic_proposal)
    _require(ok, reasons[0] if reasons else 'work_task_initial_invalid')
    b = candidate.budget
    policy = hosts.WorkTaskPolicyV01(candidate.task_id, semantic_proposal.owner_root_id, host_instance_ref,
        candidate.revision_id, candidate.intent_ref, _source_ref(source_context, semantic_proposal),
        definition_ids, tuple(sorted({i.definition_id for i in candidate.items if i.review_obligation_id is not None})),
        resource_refs, b.max_items, b.max_compute_units, b.max_children, b.max_model_calls, b.max_revisions)
    validate_installed_work_task_policy_v01(policy, owning_root_id=semantic_proposal.owner_root_id, catalogue=catalogue)
    _policy_candidate(policy, candidate, source_context, semantic_proposal)
    return policy


def _policy_candidate(policy, candidate, source_context, semantic_proposal, host=None):
    _require(type(source_context) is router.ExecutionModeSourceContextV01 and
        type(semantic_proposal) is abi.KernelArtifactV01, 'work_task_original_context')
    _require(candidate.task_id == policy.task_id and candidate.intent_ref == policy.intent_ref and
        semantic_proposal.owner_root_id == policy.owning_root_id and
        _source_ref(source_context, semantic_proposal) == policy.source_ref, 'work_task_original_context')
    resolved = () if host is None else tuple(r.definition_id for r in host.pure_need_resolutions
        if r.need.permission.task_id == policy.task_id and host._pure_permissions.get(policy.task_id) == r.need.permission)
    _require(all(i.owning_root_id == policy.owning_root_id and i.definition_id in (*policy.definition_ids, *resolved) and
        set(i.resource_refs) <= set(policy.resource_refs) for i in candidate.items), 'work_task_original_scope')
    _require(all(i.review_obligation_id is not None for i in candidate.items if i.definition_id in policy.review_definition_ids),
        'work_task_required_review_removed')
    _require(all(getattr(candidate.budget, n) <= getattr(policy, n) for n in
        ('max_items', 'max_compute_units', 'max_children', 'max_model_calls', 'max_revisions')), 'work_task_original_budget')


def _ledger(host, task_id):
    _require(type(host) is hosts.RootWorkExecutionHostV01 and task_id in host._tasks, 'work_task_not_enrolled')
    ledger = host._tasks[task_id]
    _require(type(ledger) is _TaskLedger and ledger.policy == host._task_policies[task_id], 'work_task_ledger_policy')
    return ledger


def inspect_work_task_v01(host, *, task_id):
    _require(type(host) is hosts.RootWorkExecutionHostV01, 'work_task_host_type')
    with host._lock:
        ledger = _ledger(host, task_id)
        result = hosts.WorkTaskSnapshotV01(ledger.policy, ledger.revisions[-1].program.candidate.revision_id,
            tuple(r.program.candidate.revision_id for r in ledger.revisions),
            tuple(_identity('work_terminal_history', _plain(v)) for r in ledger.revisions for v in r.results
                if v.status in ('COMPLETED', 'FAILED_NON_CONSUMING', 'UNCERTAIN_CLOSED', 'SKIPPED_GUARD_FALSE')),
            ledger.usage, ledger.outcome, ledger.reason, host.state_revision)
        _payload(_plain(result), 'task_snapshot')
        return result


def work_continuation_context_v01(host, *, task_id, expected_revision):
    snapshot = inspect_work_task_v01(host, task_id=task_id)
    _require(type(expected_revision) is int and snapshot.host_revision == expected_revision, 'work_task_stale_host_revision')
    return WorkContinuationContextV01(host, snapshot)


def _current_context(context):
    _require(type(context) is WorkContinuationContextV01 and type(context.snapshot) is hosts.WorkTaskSnapshotV01,
        'work_task_context_type')
    _require(context.snapshot == inspect_work_task_v01(context.host, task_id=context.snapshot.policy.task_id), 'work_task_stale_snapshot')
    _require(not context.host._active and context.host._task_dispatch is None, 'work_task_reentry')
    return _ledger(context.host, context.snapshot.policy.task_id)


def enroll_work_program_v01(host, program, *, catalogue, source_context, semantic_proposal, expected_revision):
    _require(type(host) is hosts.RootWorkExecutionHostV01 and type(program) is MaterializedWorkProgramV01, 'work_task_enrollment_type')
    with host._lock:
        _require(type(expected_revision) is int and expected_revision == host.state_revision and not host._active, 'work_task_stale_host_revision')
        candidate = program.candidate
        _require(candidate.task_id in host._task_policies and candidate.task_id not in host._tasks, 'work_task_enrollment_policy')
        _require(not any(a.task_id == candidate.task_id for a in host.work_attempts), 'work_task_prior_unenrolled_history')
        _require(program == materialize_work_program_v01(candidate, catalogue=catalogue, source_context=source_context,
            semantic_proposal=semantic_proposal), 'work_task_initial_materialization')
        policy = host._task_policies[candidate.task_id]
        _require(candidate.revision_id == policy.initial_revision_id, 'work_task_initial_revision')
        _policy_candidate(policy, candidate, source_context, semantic_proposal)
        _require(all(any(a is h for h in host.admitted_catalogue) for a in catalogue), 'work_task_catalogue_origin')
        host._tasks[candidate.task_id] = _TaskLedger(policy, hosts.WorkTaskUsageV01(0, 0, 0, 0, 0),
            (_TaskRevision(program, source_context, semantic_proposal, None, (), None, hosts.WorkTaskUsageV01(0, 0, 0, 0, 0), catalogue),),
            (), (), (), 'ACTIVE', None)
        host._revision += 1
        return work_continuation_context_v01(host, task_id=candidate.task_id, expected_revision=host.state_revision)


def _validate_continuation_candidate(candidate, context, catalogue, source_context, semantic_proposal):
    _require(type(context) is WorkContinuationContextV01, 'work_task_context_type')
    ledger = _ledger(context.host, candidate.task_id)
    _require(context.snapshot.policy == ledger.policy, 'work_task_foreign_snapshot')
    _policy_candidate(ledger.policy, candidate, source_context, semantic_proposal, context.host)
    accepted = [r for r in ledger.revisions if r.program.candidate.revision_id == candidate.revision_id]
    if accepted:
        _require(accepted[0].program.candidate == candidate, 'work_task_accepted_program_changed')
    else:
        _current_context(context)
        ok, reasons = (validate_pure_missing_trigger_v01(context.trigger, context=context)
            if type(context.trigger) is pure.PureMissingNeedTriggerV01 else validate_work_revision_trigger_v01(context.trigger, context=context))
        _require(ok, reasons[0] if reasons else 'work_task_trigger_invalid')
        _require(candidate.trigger_evidence_refs == (context.trigger.trigger_id,), 'work_task_trigger_refs')
        _require(candidate.previous_revision_id == ledger.revisions[-1].program.candidate.revision_id, 'work_task_predecessor')
        usage = ledger.usage
        old = ledger.revisions[-1]
        _require(candidate.budget.max_compute_units <= ledger.policy.max_compute_units - usage.compute_units and
            candidate.budget.max_children <= ledger.policy.max_children - usage.children - usage.reserved_children and
            candidate.budget.max_revisions <= ledger.policy.max_revisions - usage.revisions - 1,
            'work_task_remaining_budget')
        _require(candidate.budget.max_items <= old.program.candidate.budget.max_items and
            candidate.budget.max_compute_units <= old.program.candidate.budget.max_compute_units -
                (usage.compute_units - old.accepted_usage.compute_units) and
            candidate.budget.max_children <= old.program.candidate.budget.max_children -
                (usage.children + usage.reserved_children - old.accepted_usage.children - old.accepted_usage.reserved_children) and
            candidate.budget.max_revisions <= old.program.candidate.budget.max_revisions - 1, 'work_task_narrowed_budget')
        terminal_ids = {v.work_id for r in ledger.revisions for v in r.results if v.status in
            ('COMPLETED', 'FAILED_NON_CONSUMING', 'UNCERTAIN_CLOSED', 'SKIPPED_GUARD_FALSE')}
        _require(not terminal_ids.intersection(i.work_id for i in candidate.items), 'work_task_terminal_rewrite')
        if type(context.trigger) is pure.PureMissingNeedTriggerV01:
            _validate_pure_replacement(candidate, context, old, catalogue)


def _validate_pure_replacement(candidate, context, previous, catalogue):
    trigger = context.trigger
    original = next(i for i in previous.program.candidate.items if i.work_id == trigger.need.permission.work_id)
    replacement = next((i for i in candidate.items if i.work_id == original.work_id), None)
    _require(replacement is not None, 'pure_revision_missing_item_binding')
    completed = {r.work_id: r for r in previous.results if r.status == 'COMPLETED'}
    normalized = []
    satisfied = set()
    for binding in original.inputs:
        source = binding.source
        if type(source) is WorkOutputBindingV01 and source.predecessor_work_id in completed:
            source = build_work_historical_output_v01(context,
                revision_id=previous.program.candidate.revision_id,
                work_id=source.predecessor_work_id, output_field=source.output_field)
            ok, reasons = validate_work_historical_output_v01(source, context=context)
            _require(ok, reasons[0] if reasons else 'work_historical_invalid')
            _require(source.expected_type == binding.source.expected_type, 'work_historical_actual_field')
            satisfied.add(source.predecessor_work_id)
        normalized.append(WorkInputBindingV01(binding.input_field, source))
    # A data edge can disappear only when its exact retained result replaces it.
    # A guard on the same predecessor still requires a current DAG edge.
    if original.guard is not None:
        satisfied.discard(original.guard.predecessor_work_id)
    package = WorkInputBindingV01('package_ref', WorkLiteralV01(
        action.build_action_effect_parameter_record_v01(parameter_name='package_ref',
            value_type='REFERENCE', value=trigger.resolution.package_id)))
    expected = replace(original, definition_id=trigger.resolution.definition_id,
        inputs=tuple(sorted((*normalized, package), key=lambda b: b.input_field)),
        depends_on=tuple(p for p in original.depends_on if p not in satisfied))
    for binding in replacement.inputs:
        if type(binding.source) is WorkHistoricalOutputV01:
            ok, reasons = validate_work_historical_output_v01(binding.source, context=context)
            _require(ok, reasons[0] if reasons else 'work_historical_invalid')
    _require(replacement == expected, 'pure_revision_missing_item_binding')
    host_map = {context.host.owning_root_id: context.host}
    results = {r.work_id: r for r in previous.results}
    observed, _ = _inputs(previous.program.candidate, original, results,
        _catalogue(previous.catalogue), host_map)
    resolved, _ = _inputs(candidate, replacement, results, _catalogue(catalogue), host_map)
    _require(tuple(v for v in resolved if v.parameter_name != 'package_ref') == observed,
        'pure_revision_resolved_need_inputs')
    _require(len(observed) == 1 and observed[0].value == trigger.need.input_value,
        'pure_revision_observed_need_value')


def _validate_task_catalogue(candidate, host, catalogue):
    ledger = _ledger(host, candidate.task_id)
    accepted = next((r for r in ledger.revisions if r.program.candidate.revision_id == candidate.revision_id), None)
    expected = accepted.catalogue if accepted is not None else host.admitted_catalogue
    _require(type(catalogue) is tuple and len(catalogue) == len(expected) and
        all(a is b for a,b in zip(catalogue, expected)), 'pure_catalogue_exact_membership')
    epoch = candidate.catalogue_revision
    _require(epoch < len(host.catalogue_membership_history) and
        len(host.catalogue_membership_history[epoch]) == len(catalogue) and
        all(a is b for a,b in zip(catalogue, host.catalogue_membership_history[epoch])), 'pure_catalogue_epoch')


def build_pure_need_permission_v01(program, *, catalogue, source_context, semantic_proposal,
    work_id, memory_scope, max_generation_attempts=2, max_admissions=3, max_drs_bytes=131072):
    _require(program == materialize_work_program_v01(program.candidate, catalogue=catalogue,
        source_context=source_context, semantic_proposal=semantic_proposal), 'pure_permission_materialization')
    item = next(i for i in program.candidate.items if i.work_id == work_id)
    _require(item.definition_id == pure.MISSING_DEFINITION and item.definition_id not in _catalogue(catalogue)
        and item.review_obligation_id is None and not item.resource_refs, 'pure_permission_missing_item')
    payload = abi.kernel_artifact_to_plain_dict_v01(semantic_proposal)['payload']
    need = payload['pure_need']
    _require(type(need) is dict and set(need) == {'contract_version','work_id','multiplier','offset'}
        and need['work_id'] == item.work_id, 'pure_permission_semantic_need')
    permission = pure.PureNeedPermissionV01(program.candidate.task_id,item.owning_root_id,
        program.candidate.revision_id,_source_ref(source_context,semantic_proposal),work_id,
        need['contract_version'],need['multiplier'],need['offset'],memory_scope,pure.worker.PROFILE_VERSION,
        max_generation_attempts,max_admissions,max_drs_bytes)
    pure.validate_pure_need_permission_v01(permission)
    return permission


def observe_missing_pure_need_v01(context):
    from dataclasses import asdict
    ledger = _current_context(context)
    permission = context.host._pure_permissions.get(ledger.policy.task_id)
    _require(permission is not None and permission.source_ref == ledger.policy.source_ref, 'pure_task_permission_absent')
    record = ledger.revisions[-1]
    _require(record.artifact is not None and ledger.outcome == 'NEEDS_CAPABILITY', 'pure_need_not_observed')
    item = next((i for i in record.program.candidate.items if i.work_id == permission.work_id), None)
    observation = next((r for r in record.results if r.work_id == permission.work_id), None)
    _require(item is not None and item.definition_id == pure.MISSING_DEFINITION and
        item.definition_id not in _catalogue(context.host.admitted_catalogue) and observation is not None
        and observation.status == 'NEEDS_CAPABILITY' and observation.invocation is None
        and observation.result is None, 'pure_missing_observation_binding')
    values, refs = _inputs(record.program.candidate,item,{r.work_id:r for r in record.results},
        _catalogue(record.catalogue),{context.host.owning_root_id:context.host})
    _require(len(values) == 1 and values[0].parameter_name == 'value' and values[0].value_type == 'INTEGER', 'pure_need_resolved_input')
    need = pure.PureCapabilityNeedV01('',permission,record.program.candidate.revision_id,
        record.program.topology_artifact.artifact_id,_identity('pure_missing_observation',
            [_plain(observation),record.artifact.artifact_id,[_plain(v) for v in values],[_plain(r) for r in refs]]),values[0].value)
    material = asdict(need)
    del material['need_id']
    need = replace(need,need_id=pure.pure_evidence_identity_v01('pure_need',material))
    pure.validate_pure_need_v01(need)
    return need


def validate_current_pure_need_v01(host, *, need):
    pure.validate_pure_need_v01(need)
    context = work_continuation_context_v01(host,task_id=need.permission.task_id,expected_revision=host.state_revision)
    _require(observe_missing_pure_need_v01(context) == need, 'pure_need_current_binding')
    return True


def build_pure_missing_trigger_v01(context, *, need, resolution):
    from dataclasses import asdict
    _current_context(context)
    validate_current_pure_need_v01(context.host,need=need)
    pure.validate_pure_resolution_v01(resolution)
    _require(type(resolution) is pure.PureNeedResolutionV01 and any(resolution is r for r in
        context.host.pure_need_resolutions) and resolution.need == need, 'pure_trigger_resolution_origin')
    trigger = pure.PureMissingNeedTriggerV01(pure.pure_evidence_identity_v01('pure_missing_trigger',
        dict(need=asdict(need),resolution=asdict(resolution))),need,resolution)
    pure.validate_pure_missing_trigger_shape_v01(trigger)
    _payload(dict(trigger_id=trigger.trigger_id,need_id=need.need_id,resolution_id=resolution.resolution_id,
        task_id=need.permission.task_id,revision_id=need.revision_id), 'pure_missing_trigger')
    return trigger


def validate_pure_missing_trigger_v01(trigger, *, context):
    try:
        _require(type(trigger) is pure.PureMissingNeedTriggerV01, 'pure_trigger_type')
        expected = build_pure_missing_trigger_v01(context,need=trigger.need,resolution=trigger.resolution)
        _require(expected == trigger and trigger.need.revision_id == context.snapshot.current_revision_id, 'pure_trigger_predecessor')
        package = context.host._pure_packages[trigger.resolution.admission_id]
        pure.validate_admitted_pure_package_v01(package,host=context.host,need=trigger.need)
        _require(trigger.resolution.membership_epoch == len(context.host.catalogue_membership_history)-1,
            'pure_trigger_current_membership')
        return True, ()
    except (ValueError,TypeError,AttributeError,KeyError,jsonschema.ValidationError) as exc:
        return False, (str(exc),)


def _historical_value(host, binding, consumer, definitions):
    _require(type(binding) is WorkHistoricalOutputV01, 'work_historical_type')
    _payload(_plain(binding), 'historical_output')
    ledger = _ledger(host, binding.task_id)
    allowed = (*ledger.policy.definition_ids, *(r.definition_id for r in host.pure_need_resolutions
        if r.need.permission.task_id == binding.task_id and host._pure_permissions.get(binding.task_id) == r.need.permission))
    _require(consumer.owning_root_id == ledger.policy.owning_root_id and consumer.definition_id in allowed,
        'work_historical_current_scope')
    records = [r for r in ledger.revisions if r.program.candidate.revision_id == binding.revision_id]
    _require(len(records) == 1, 'work_historical_revision')
    record = records[0]
    item = next((i for i in record.program.candidate.items if i.work_id == binding.predecessor_work_id), None)
    value = next((r for r in record.results if r.work_id == binding.predecessor_work_id), None)
    _require(item is not None and value is not None and record.artifact is not None, 'work_historical_not_observed')
    _require(_source_ref(record.source_context, record.semantic_proposal) == ledger.policy.source_ref, 'work_historical_source')
    original_definitions = _catalogue(record.catalogue) if host._pure_permissions else definitions
    _validate_completed(record.program.candidate, item, value, original_definitions, {host.owning_root_id: host})
    _require((binding.invocation_id, binding.result_id, binding.admission_id, binding.result_artifact_ref) ==
        (value.invocation.invocation_id, value.result.result_id, value.invocation.admission_id, record.artifact.artifact_id),
        'work_historical_provenance')
    _require(not abi.validate_kernel_artifact_v01(record.artifact) and
        abi.kernel_artifact_to_plain_dict_v01(record.artifact)['payload']['work_results'] == [_plain(v) for v in record.results],
        'work_historical_artifact')
    actual = next((v for v in value.result.output if v.parameter_name == binding.output_field), None)
    _require(actual is not None and actual == binding.value and actual.value_type == binding.expected_type, 'work_historical_actual_field')
    return actual


def build_work_historical_output_v01(context, *, revision_id, work_id, output_field):
    ledger = _current_context(context)
    record = next((r for r in ledger.revisions if r.program.candidate.revision_id == revision_id), None)
    _require(record is not None and record.artifact is not None, 'work_historical_revision')
    value = next((v for v in record.results if v.work_id == work_id), None)
    _require(value is not None and value.status == 'COMPLETED', 'work_historical_not_completed')
    field = next((v for v in value.result.output if v.parameter_name == output_field), None)
    _require(field is not None, 'work_historical_field')
    binding = WorkHistoricalOutputV01(ledger.policy.task_id, revision_id, work_id, value.invocation.invocation_id,
        value.result.result_id, value.invocation.admission_id, record.artifact.artifact_id, output_field, field.value_type, field)
    producer = next(i for i in record.program.candidate.items if i.work_id == work_id)
    _historical_value(context.host, binding, producer, _catalogue(context.host.admitted_catalogue))
    return binding


def build_work_revision_trigger_v01(context, *, work_id, output_field):
    output = build_work_historical_output_v01(context, revision_id=context.snapshot.current_revision_id,
        work_id=work_id, output_field=output_field)
    return WorkRevisionTriggerV01(_identity('work_revision_trigger', _plain(output)), output)


def validate_work_task_snapshot_v01(snapshot, *, host):
    try:
        _require(type(snapshot) is hosts.WorkTaskSnapshotV01, 'work_task_snapshot_type')
        _require(snapshot == inspect_work_task_v01(host, task_id=snapshot.policy.task_id), 'work_task_stale_snapshot')
        return True, ()
    except (ValueError, TypeError, AttributeError, KeyError, jsonschema.ValidationError) as exc:
        return False, (str(exc) if isinstance(exc, ValueError) else 'work_task_snapshot_shape',)


def validate_work_historical_output_v01(binding, *, context):
    try:
        ledger = _current_context(context)
        _require(type(binding) is WorkHistoricalOutputV01 and binding.task_id == ledger.policy.task_id, 'work_historical_foreign_task')
        record = next((r for r in ledger.revisions if r.program.candidate.revision_id == binding.revision_id), None)
        _require(record is not None, 'work_historical_revision')
        item = next((i for i in record.program.candidate.items if i.work_id == binding.predecessor_work_id), None)
        _require(item is not None, 'work_historical_not_observed')
        _historical_value(context.host, binding, item, _catalogue(context.host.admitted_catalogue))
        return True, ()
    except (ValueError, TypeError, AttributeError, KeyError, jsonschema.ValidationError) as exc:
        return False, (str(exc) if isinstance(exc, ValueError) else 'work_historical_shape',)


def validate_work_revision_trigger_v01(trigger, *, context):
    try:
        ledger = _current_context(context)
        _require(type(trigger) is WorkRevisionTriggerV01 and type(trigger.output) is WorkHistoricalOutputV01, 'work_task_trigger_required')
        _payload(_plain(trigger), 'revision_trigger')
        _require(trigger.output.task_id == ledger.policy.task_id and trigger.output.revision_id ==
            ledger.revisions[-1].program.candidate.revision_id, 'work_task_trigger_predecessor')
        _require(trigger.trigger_id == _identity('work_revision_trigger', _plain(trigger.output)), 'work_task_trigger_identity')
        ok, reasons = validate_work_historical_output_v01(trigger.output, context=context)
        _require(ok, reasons[0] if reasons else 'work_task_trigger_not_observed')
        return True, ()
    except (ValueError, TypeError, AttributeError, KeyError, jsonschema.ValidationError) as exc:
        return False, (str(exc) if isinstance(exc, ValueError) else 'work_task_trigger_shape',)


def _exhaust_task(host, task_id, reason):
    ledger = _ledger(host, task_id)
    host._tasks[task_id] = replace(ledger, outcome='EXHAUSTED', reason=reason)
    host._revision += 1
    host._events.append(('TASK_EXHAUSTED', host.state_revision, task_id, reason))


def _task_outcome(host, task_id):
    ledger = _ledger(host, task_id)
    current = ledger.revisions[-1]
    return WorkContinuationOutcomeV01(current.program, current.results, inspect_work_task_v01(host, task_id=task_id),
        ledger.outcome, ledger.reason)


def inspect_work_task_history_v01(context):
    ledger = _current_context(context)
    return tuple((r.program, r.results, r.artifact, r.trigger) for r in ledger.revisions)


def inspect_work_task_review_v01(context, *, obligation_id):
    """Original observed CONTROL evidence, not approval of the current work."""
    ledger = _current_context(context)
    result = next((r for r in ledger.reviews if r[0].obligation_id == obligation_id), None)
    _require(result is not None, 'work_task_review_not_observed')
    return result


def inspect_work_continuation_outcome_v01(context):
    """Read the retained result at the current host revision without dispatch."""
    _require(type(context) is WorkContinuationContextV01, 'work_task_context_type')
    with context.host._lock:
        ledger = _current_context(context)
        return _task_outcome(context.host, ledger.policy.task_id)


def validate_work_continuation_outcome_v01(value, *, context, catalogue, source_context, semantic_proposal, review_bindings=()):
    try:
        ledger = _current_context(context)
        _require(type(value) is WorkContinuationOutcomeV01 and value == _task_outcome(context.host, ledger.policy.task_id),
            'work_task_outcome_binding')
        if value.status != 'EXHAUSTED':
            ok, reasons = validate_work_program_result_v01(value.program, value.results, catalogue=catalogue,
                host_map={context.host.owning_root_id: context.host}, source_context=source_context,
                semantic_proposal=semantic_proposal, review_bindings=review_bindings, continuation_context=context)
            _require(ok, reasons[0] if reasons else 'work_task_result_invalid')
        else:
            _require(value.reason in ('work_task_revision_exhausted', 'work_task_compute_exhausted', 'work_task_children_exhausted'),
                'work_task_exhaustion_reason')
        _payload(dict(program=_plain(value.program.candidate), results=[_plain(r) for r in value.results],
            snapshot=_plain(value.snapshot), status=value.status, reason=value.reason), 'continuation_outcome')
        return True, ()
    except (ValueError, TypeError, AttributeError, KeyError, jsonschema.ValidationError) as exc:
        return False, (str(exc) if isinstance(exc, ValueError) else 'work_task_outcome_shape',)


def revise_work_program_v01(context, *, previous_revision_id, trigger, items, budget,
    catalogue, source_context, semantic_proposal):
    _require(type(context) is WorkContinuationContextV01, 'work_task_context_type')
    with context.host._lock:
        ledger = _current_context(context)
        old = ledger.revisions[-1].program.candidate
        _require(previous_revision_id == old.revision_id, 'work_task_predecessor')
        missing_trigger = type(trigger) is pure.PureMissingNeedTriggerV01
        if missing_trigger:
            ok, reasons = validate_pure_missing_trigger_v01(trigger, context=context)
            _require(ok, reasons[0] if reasons else 'pure_trigger_invalid')
        else:
            _require(type(trigger) is WorkRevisionTriggerV01 and type(trigger.output) is WorkHistoricalOutputV01, 'work_task_trigger_required')
            _require(trigger.output.task_id == old.task_id and trigger.output.revision_id == old.revision_id, 'work_task_trigger_predecessor')
            _require(trigger.trigger_id == _identity('work_revision_trigger', _plain(trigger.output)), 'work_task_trigger_identity')
            producer = next((i for i in old.items if i.work_id == trigger.output.predecessor_work_id), None)
            _require(producer is not None, 'work_task_trigger_work')
            _historical_value(context.host, trigger.output, producer, _catalogue(catalogue))
        if ledger.outcome == 'EXHAUSTED':
            return _task_outcome(context.host, old.task_id)
        if ledger.usage.revisions >= ledger.policy.max_revisions or old.budget.max_revisions == 0:
            _exhaust_task(context.host, old.task_id, 'work_task_revision_exhausted')
            return _task_outcome(context.host, old.task_id)
        current = ledger.revisions[-1]
        if ledger.usage.compute_units >= ledger.policy.max_compute_units or ledger.usage.compute_units - current.accepted_usage.compute_units >= old.budget.max_compute_units:
            _exhaust_task(context.host, old.task_id, 'work_task_compute_exhausted')
            return _task_outcome(context.host, old.task_id)
        candidate = build_work_program_candidate_v01(task_id=old.task_id, previous_revision_id=previous_revision_id,
            intent_ref=old.intent_ref, bsep_ref=old.bsep_ref, semantic_proposal_ref=old.semantic_proposal_ref,
            catalogue_revision=trigger.resolution.membership_epoch if missing_trigger else old.catalogue_revision,
            budget=budget, items=items, trigger_evidence_refs=(trigger.trigger_id,),
            catalogue=catalogue, source_context=source_context, semantic_proposal=semantic_proposal, continuation_context=replace(context, trigger=trigger))
        program = materialize_work_program_v01(candidate, catalogue=catalogue, source_context=source_context,
            semantic_proposal=semantic_proposal, continuation_context=replace(context, trigger=trigger))
        if not missing_trigger:
            _require(any(type(b.source) is WorkHistoricalOutputV01 and b.source == trigger.output for i in items for b in i.inputs),
                'work_task_trigger_not_consumed')
        usage = replace(ledger.usage, revisions=ledger.usage.revisions + 1)
        context.host._tasks[old.task_id] = replace(ledger, usage=usage, outcome='ACTIVE', reason=None,
            revisions=(*ledger.revisions, _TaskRevision(program, source_context, semantic_proposal, trigger, (), None, usage, catalogue)))
        context.host._revision += 1
        return _task_outcome(context.host, old.task_id)


def _charge_task_dispatch_v01(host, task_id, instance, admission_id, inputs):
    ledger = _ledger(host, task_id)
    _require(host._task_dispatch == (task_id, instance, admission_id, inputs), 'work_task_dispatch_context_required')
    _require(instance not in ledger.charged_instances, 'work_task_already_charged')
    if ledger.outcome == 'EXHAUSTED' or ledger.usage.compute_units >= ledger.policy.max_compute_units:
        _exhaust_task(host, task_id, 'work_task_compute_exhausted')
        raise _TaskExhausted('work_task_compute_exhausted')
    host._tasks[task_id] = replace(ledger, usage=replace(ledger.usage, compute_units=ledger.usage.compute_units + 1),
        charged_instances=(*ledger.charged_instances, instance))
    host._revision += 1
    host._events.append(('TASK_COMPUTE_RESERVED', host.state_revision, task_id, instance))


def _retain_task_result(host, program, value):
    ledger = _ledger(host, program.candidate.task_id)
    current = ledger.revisions[-1]
    prior = {r.work_id: r for r in current.results}
    if value.work_id in prior and prior[value.work_id].status in ('COMPLETED', 'FAILED_NON_CONSUMING', 'UNCERTAIN_CLOSED', 'SKIPPED_GUARD_FALSE'):
        _require(value == prior[value.work_id], 'work_task_terminal_rewrite')
    prior[value.work_id] = value
    current = replace(current, results=tuple(prior[w] for w in program.ordered_work_ids if w in prior))
    host._tasks[program.candidate.task_id] = replace(ledger, revisions=(*ledger.revisions[:-1], current))


def advance_work_program_v01(program, *, catalogue, source_context, semantic_proposal,
    host_map, results=(), review_bindings=(), action_authorizers=None, continuation_context=None):
    kwargs = dict(catalogue=catalogue, source_context=source_context, semantic_proposal=semantic_proposal,
        host_map=host_map, results=results, review_bindings=review_bindings, action_authorizers=action_authorizers)
    if continuation_context is None:
        _require(not any(type(h) is hosts.RootWorkExecutionHostV01 and h._task_policies for h in host_map.values()),
            'work_task_context_required')
        return _advance_work_program_v01(program, **kwargs)
    _require(type(continuation_context) is WorkContinuationContextV01, 'work_task_context_type')
    host = continuation_context.host
    with host._lock:
        ledger = _current_context(continuation_context)
        task_id = ledger.policy.task_id
        _require(program == ledger.revisions[-1].program and host_map == {host.owning_root_id: host}, 'work_task_current_program')
        _require(results == ledger.revisions[-1].results, 'work_task_history_omitted')
        if ledger.outcome == 'EXHAUSTED':
            return _task_outcome(host, task_id)
        for item in program.candidate.items:
            if item.review_obligation_id is not None:
                _require(any(o.obligation_id == item.review_obligation_id and (o, s, b) in review_bindings
                    for o, s, b in ledger.reviews), 'work_task_review_not_observed')
        before = (host.state_revision, ledger)
        try:
            output = _advance_work_program_v01(program, **kwargs, continuation_context=continuation_context)
            ledger = _ledger(host, task_id)
            current = ledger.revisions[-1]
            artifact = work_program_result_to_artifact_v01(program, output, catalogue=catalogue, host_map=host_map,
                source_context=source_context, semantic_proposal=semantic_proposal, review_bindings=review_bindings,
                continuation_context=continuation_context)
            status = 'COMPLETED' if all(r.status in ('COMPLETED', 'SKIPPED_GUARD_FALSE') for r in output) else (
                'NEEDS_CAPABILITY' if any(r.status == 'NEEDS_CAPABILITY' for r in output) else 'ACTIVE')
            host._tasks[task_id] = replace(ledger, revisions=(*ledger.revisions[:-1], replace(current, results=output, artifact=artifact)), outcome=status)
            if host._tasks[task_id] != before[1] and host.state_revision == before[0]:
                host._revision += 1
            return _task_outcome(host, task_id)
        except _TaskExhausted:
            return _task_outcome(host, task_id)
        finally:
            host._task_dispatch = None


def execute_work_task_review_v01(context, *, obligation, source_context, semantic_proposal):
    """Fixed public D execution, never a caller-provided privileged executor."""
    _require(type(context) is WorkContinuationContextV01, 'work_task_context_type')
    host = context.host
    with host._lock:
        ledger = _current_context(context)
        if ledger.outcome == 'EXHAUSTED':
            return _task_outcome(host, ledger.policy.task_id)
        current = ledger.revisions[-1]
        candidate = current.program.candidate
        item = next((i for i in candidate.items if i.review_obligation_id == obligation.obligation_id), None)
        _require(item is not None and obligation == build_work_review_obligation_v01(candidate=candidate,
            item=item, source_context=source_context), 'work_task_review_context')
        _require(_source_ref(source_context.g2c_source_context, semantic_proposal) == ledger.policy.source_ref, 'work_task_review_source')
        scope = build_work_review_scope_ref_v01(candidate=candidate, item=item,
            source_context=source_context.g2c_source_context, semantic_proposal=semantic_proposal)
        _require(source_context.decision.accepted_scope_ref == scope and
            fractal.validate_fractal_runtime_source_context_v02(source_context).status == 'PASS', 'work_task_review_source')
        old = next((r for r in ledger.reviews if r[0] == obligation and r[1] == source_context), None)
        if old is not None:
            return old
        # Reserve the public source policy's whole child ceiling, not a caller's
        # claimed eventual count. Release only known unused capacity on success.
        reservation = source_context.runtime_policy.max_total_cells - 1
        original_remaining = ledger.policy.max_children - ledger.usage.children - ledger.usage.reserved_children
        revision_remaining = candidate.budget.max_children - (ledger.usage.children + ledger.usage.reserved_children -
            current.accepted_usage.children - current.accepted_usage.reserved_children)
        if reservation > min(original_remaining, revision_remaining):
            _exhaust_task(host, candidate.task_id, 'work_task_children_exhausted')
            return _task_outcome(host, candidate.task_id)
        host._tasks[candidate.task_id] = replace(ledger, usage=replace(ledger.usage,
            reserved_children=ledger.usage.reserved_children + reservation))
        host._revision += 1
        host._events.append(('TASK_D_REVIEW_RESERVED', host.state_revision, candidate.task_id, obligation.obligation_id, reservation))
        bundle, report = fractal.run_fractal_runtime_v02(source_context)
        _require(report.status == 'PASS' and bundle is not None, 'work_task_review_execution')
        ok, reasons = validate_work_review_binding_v01(obligation, candidate=candidate, item=item,
            source_context=source_context, execution_bundle=bundle, semantic_proposal=semantic_proposal)
        _require(ok, reasons[0] if reasons else 'work_task_review_invalid')
        children = len(bundle.cell_results) - 1
        _require(0 <= children <= reservation, 'work_task_review_accounting')
        ledger = _ledger(host, candidate.task_id)
        receipt = (obligation, source_context, bundle)
        host._tasks[candidate.task_id] = replace(ledger, usage=replace(ledger.usage, children=ledger.usage.children + children,
            reserved_children=ledger.usage.reserved_children - reservation), reviews=(*ledger.reviews, receipt))
        host._revision += 1
        host._events.append(('TASK_D_REVIEW_COMPLETED', host.state_revision, candidate.task_id, bundle.runtime_report.report_id, children))
        return receipt
