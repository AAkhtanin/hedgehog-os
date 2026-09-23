"""G4-0 finite enrolled Airline Work and independent preparation-only reviews.

No strategy mathematics, effect dispatch, provider, history write or admission
of repository sources. Evidence on disk never reconstructs a Host origin.
"""
from contextlib import contextmanager
from dataclasses import fields, is_dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from hedgehog import action_commit_packet_v02 as actions
from hedgehog import work_execution_host_v01 as hosts
from hedgehog import outcome_feedback_v01 as feedback
from hedgehog import outcome_feedback_history_v01 as history
from hedgehog import outcome_calibration_v01 as calibration
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import work_composition_v01 as work
from hedgehog.kernel import root_decision_v01 as roots
from hedgehog.kernel import semantic_work_v01 as semantic
from hedgehog.kernel import trust_model_v01 as trust
from hedgehog.kernel import multiroot_v01 as multi
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from . import semantic_to_contract_binding_v01 as binding
from . import incident_atlas_work_v01 as checks
from .incident_atlas_source_v01 import current_source_v01


ROOT = binding.CLIENT_ROOT_ID
ROOTS = (ROOT, binding.AIRLINE_ROOT_ID, binding.BANK_ROOT_ID)
PROFILE = 'G4_REFERENCE_SCOPE_V01'


def require_v01(condition, reason):
    if not condition:
        raise ValueError(reason)


def plain_v01(value):
    """Evidence-only projection; callers must never pass live Host handles."""
    if type(value) is abi.KernelArtifactV01:
        return abi.kernel_artifact_to_plain_dict_v01(value)
    if type(value) is roots.RootDecisionInputV01:
        return roots.root_decision_input_to_plain_dict_v01(value)
    if type(value) is roots.RootDecisionKernelV01:
        return roots.root_decision_kernel_to_plain_dict_v01(value)
    if type(value) is roots.RootDecisionResultV01:
        return roots.root_decision_result_to_plain_dict_v01(value)
    if value is None or type(value) in (str, int, bool, float):
        return value
    if type(value) in (tuple, list):
        return [plain_v01(v) for v in value]
    if type(value) is dict:
        return {k: plain_v01(v) for k, v in value.items()}
    require_v01(is_dataclass(value) and not isinstance(value, type), 'g40_plain_type')
    return {f.name: plain_v01(getattr(value, f.name)) for f in fields(value)}


def canonical_v01(value):
    return canonical_json_bytes_v01(plain_v01(value))


def digest_v01(value):
    return hashlib.sha256(canonical_v01(value)).hexdigest()


def utc_v01(second):
    return datetime.fromtimestamp(second, timezone.utc).isoformat(timespec='seconds')


def fixture_v01():
    return json.loads((Path(__file__).resolve().parents[3] / 'fixtures/gate4_reference_v01.json').read_bytes())


def provenance_result_v01(inputs):
    values = {v.parameter_name: json.loads(v.value) for v in inputs}
    expected = checks.evaluate_v01(values['material'])
    require_v01(values['previous'] == expected, 'g40_previous_constraint_binding')
    return checks.evaluate_v01(values['material'], provenance=True)


def provenance_input_validator_v01(definition, inputs):
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    if not errors:
        try:
            provenance_result_v01(inputs)
        except (ValueError, TypeError, KeyError):
            errors = ('g40_provenance_input',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,
        values=inputs, invocation_id=None, valid=not errors, reason_codes=errors)


def execute_provenance_v01(invocation):
    return (actions.ActionEffectParameterRecordV01('material', 'TEXT',
        canonical_v01(provenance_result_v01(invocation.inputs)).decode()),)


def provenance_output_validator_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors and json.loads(output[0].value) != provenance_result_v01(invocation.inputs):
        errors = ('g40_provenance_output',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,
        values=output, invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def catalogue_v01():
    # The existing constraint definition is reused unchanged. The new provenance
    # quantum consumes that actual output, not a caller-supplied healthy flag.
    original = checks.catalogue_v01()
    functions = (provenance_input_validator_v01, provenance_output_validator_v01, execute_provenance_v01)
    codes = tuple(hosts.observe_local_capability_code_v01(f) for f in functions)
    field = lambda name: firewall.build_capability_field_v01(name=name, value_type='TEXT', required=True, consequential=False)
    definition = firewall.build_capability_definition_v01(operation_id='g40.airline.provenance',
        version='v01', effect_kind='PURE', business_semantics=None,
        input_fields=(field('material'), field('previous')), output_fields=(field('material'),), resource_refs=(),
        input_validator_ref=codes[0].public_symbol, output_validator_ref=codes[1].public_symbol,
        executor_ref=codes[2].public_symbol, code_sha256s=tuple((v.public_symbol, v.source_sha256) for v in codes))
    admitted = hosts.admit_local_capability_v01(definition=definition, input_validator=functions[0],
        output_validator=functions[1], executor=functions[2], catalogue_revision=0, host_instance_ref='host:' + ROOT)
    return original + (admitted,)


def controlled_source_v01(config, now, invocation):
    constraints = replace(binding.build_client_constraints_preference_a_v01(),
        constraint_set_id='g40:constraints:' + invocation, max_amount=config['max_amount'])
    old = binding.build_airline_candidate_snapshot_v01()
    records = tuple(replace(record, offer_id='g40:offer:' + str(i), amount=amount)
        for i, (record, amount) in enumerate(zip(old.authoritative_offer_records[:2], config['offer_amounts'])))
    snapshot = replace(old, candidate_set_ref='g40:offers:' + invocation,
        candidate_set_snapshot_id='g40:snapshot:' + invocation, authoritative_offer_records=records,
        snapshot_created_at=utc_v01(now), snapshot_ttl_seconds=config['snapshot_ttl_seconds'])
    snapshot = replace(snapshot, candidate_set_digest=binding.compute_airline_candidate_set_digest_v01(snapshot))
    selection = binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(), constraints, snapshot)
    reports = (binding.validate_airline_candidate_snapshot_v01(snapshot),
        binding.validate_client_root_travel_constraint_set_v01(constraints),
        binding.validate_airline_semantic_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(), constraints, snapshot, selection))
    require_v01(all(r.validation_status == 'PASS' for r in reports), 'g40_domain_source')
    require_v01(len(selection.client_hard_compatible_candidate_ids) >= 2, 'g40_two_compatible_offers')
    # This is a declared existing client price preference, not Nash or a forced
    # fixture winner. Both compatible alternatives remain in the saved source.
    selected = min((r for r in records if r.offer_id in selection.client_hard_compatible_candidate_ids),
        key=lambda r: (r.amount, r.offer_id))
    return constraints, snapshot, selection, selected, reports


def consume_v01(live, *, constraints, snapshot, selected_offer_id):
    for program, results, common in live['programs']:
        valid, reasons = work.validate_work_program_result_v01(program, results, **common, host_map={ROOT: live['host']})
        require_v01(valid, 'g40_public_work:' + repr(reasons))
    material = checks.material_v01(constraints, snapshot, selected_offer_id, live['semantic_ref'])
    require_v01(selected_offer_id == live['output']['offer_id'], 'g40_selected_offer_binding')
    require_v01(canonical_v01(material) == live['material'], 'g40_current_source_binding')
    require_v01(live['output'] == checks.evaluate_v01(material), 'g40_constraint_consumption')
    require_v01(live['provenance'] == checks.evaluate_v01(material, provenance=True), 'g40_provenance_consumption')
    require_v01(live['output']['checks'][0]['healthy'] and live['provenance']['provenance_checked'], 'g40_useful_output')
    return material


def review_v01(live, *, root, constraints, snapshot, selected, consent, bank_limit, now):
    material = consume_v01(live, constraints=constraints, snapshot=snapshot, selected_offer_id=selected.offer_id)
    artifact = live['artifact']; ref = artifact.artifact_id
    provenance_ref = live['provenance_artifact'].artifact_id
    terms_ref = 'g40:terms:' + digest_v01(selected)
    local = dict(root=root, offer=plain_v01(selected), source=snapshot.candidate_set_digest,
        constraints=plain_v01(constraints), consent=consent, bank_limit=bank_limit, now=now,
        result_ref=ref, provenance_result_ref=provenance_ref)
    local_ref = 'g40:local:' + digest_v01(local)
    refs = (ref, provenance_ref, terms_ref, snapshot.candidate_set_snapshot_id, local_ref)
    actor = 'g40:local_validator:' + root
    request = semantic.build_semantic_work_request_v01(request_id='g40:request:' + digest_v01(local),
        transaction_id=artifact.transaction_id, target_root_id=root,
        runtime_topology_ref=live['programs'][0][0].topology_artifact.artifact_id,
        bounded_context_refs=refs, permitted_actor_ids=(actor,), permitted_contribution_modes=('DETERMINISTIC',),
        requested_subjects=(selected.offer_id,), required_evidence_classes=('DEPENDENCY_EVIDENCE',), forbidden_claims=('authority_creation',))
    evidence = tuple(semantic.build_evidence_binding_v01(evidence_id='binding:' + r, evidence_ref=r,
        evidence_class='DEPENDENCY_EVIDENCE', source_component_id=actor, provenance_ref=local_ref, evidence_state='PRESENT') for r in refs)
    claim = semantic.build_normalized_claim_v01(claim_id=ref, subject=selected.offer_id,
        predicate='g40_actual_constraint_result_for_preparation', object_or_value=live['output'],
        time_envelope_ref='g40:time:' + str(now), provenance_refs=refs,
        evidence_refs=tuple(e.evidence_id for e in evidence), confidence_micros=1000000,
        source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    contribution = semantic.build_actor_contribution_v01(contribution_id='g40:contribution:' + digest_v01(local),
        request_id=request.request_id, actor_id=actor, actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC',
        bsep_projection_ref=live['source'].bsep_packet['packet_id'], scope=selected.offer_id,
        bounded_context_refs=refs, claims=(claim,), evidence_bindings=evidence, constraint_bindings=(), uncertainty_bindings=(),
        requested_validators=('g40:current_source_and_actual_work',), forbidden_claims_observed=())
    packet = semantic.build_root_review_packet_from_contributions_v01(request=request, contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    selection = binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(), constraints, snapshot)
    policies = {
        ROOT: selected.offer_id in selection.client_hard_compatible_candidate_ids,
        binding.AIRLINE_ROOT_ID: selected.inventory_available and selected.airline_policy_valid,
        binding.BANK_ROOT_ID: selected.amount <= bank_limit and selected.currency == constraints.currency,
    }
    require_v01(root in policies, 'g40_local_root_scope')
    required = root in (ROOT, binding.BANK_ROOT_ID)
    permission_scope = (not consent or (consent['root_id'] == root and consent['offer_id'] == selected.offer_id
        and consent['source_digest'] == snapshot.candidate_set_digest and selected.amount <= consent['max_amount']
        and consent['currency'] == selected.currency and consent['purpose'] == 'PREPARATION_ONLY'))
    created = int(datetime.fromisoformat(snapshot.snapshot_created_at.replace('Z', '+00:00')).timestamp())
    fresh = created <= now < created + min(snapshot.snapshot_ttl_seconds, selected.ttl_seconds)
    kernel = roots.build_root_decision_kernel_v01()
    decision_input = roots.build_root_decision_input_v01(transaction_id=artifact.transaction_id, target_root_id=root,
        root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=local_ref, post_vv_passed=bool(material), validated_candidate_ids=[ref], rejected_candidate_ids=[],
            required_evidence_refs=list(refs), provided_evidence_refs=list(refs), hard_failure_reasons=[]),
        gt_advisory=dict(advisory_id='g40:advisory:' + digest_v01(local), candidate_ids=[ref], selected_candidate_id=ref,
            score_micros_by_candidate={ref:1000000}, source_artifact_type='GTAdvisoryReport', source_lifecycle_state='VALIDATED',
            actor_role='gt', attempted_effect='CREATE_ROOT_DECISION', target_artifact_type='RootDecision', advisory_only=True,
            creates_final_output=False, requests_effect=False),
        policy_state=dict(policy_id='g40:local_preparation:' + root, identity_passed=root in ROOTS,
            scope_passed=selected in snapshot.authoritative_offer_records, hard_policy_passed=policies[root],
            allow_accept=policies[root], conflict_policy='DEFER', no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=required, user_permission_present=consent is not None,
            permission_scope_valid=bool(permission_scope), permission_ref='g40:consent:' + digest_v01(consent) if consent else None),
        temporal_state=dict(temporal_valid=fresh, expired=not fresh or snapshot.snapshot_expired or selected.expired,
            not_before_satisfied=now >= created, time_envelope_ref='g40:time:' + str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids), conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None, prior_decision=None, prior_selected_candidate_id=None))
    result = roots.decide_root_v01(kernel=kernel, decision_input=decision_input)
    require_v01(not roots.validate_root_decision_result_v01(kernel=kernel, decision_input=decision_input, result=result), 'g40_root_validation')
    return (kernel, decision_input, result), local


def multiroot_v01(reviews, offer_id):
    envelopes = tuple(multi.build_root_decision_envelope_v01(transaction_id=review[1].transaction_id,
        root_id=root, root_decision_id=review[2].decision_id, source_decision_ref=review[1].decision_input_id,
        outcome_class={'ACCEPT':'ACCEPTED', 'REJECT':'REJECTED', 'DEFER':'DEFERRED',
            'BLOCKED_FAIL_CLOSED':'BLOCKED'}.get(review[2].decision, review[2].decision),
        reason_code=review[2].reason_code, selected_subject_id=offer_id if review[2].decision == 'ACCEPT' else None,
        evidence_refs=(review[1].root_review_packet.runtime_topology_ref,), cross_root_input_refs=()) for root, review in reviews.items())
    outcome = multi.build_transaction_outcome_envelope_v01(transaction_id=envelopes[0].transaction_id,
        expected_root_ids=ROOTS, root_decisions=envelopes, cross_root_evidence_refs=())
    require_v01(not multi.validate_transaction_outcome_envelope_v01(outcome), 'g40_multiroot_validation')
    return multi.transaction_outcome_envelope_to_plain_dict_v01(outcome), multi.multiroot_validation_result_to_plain_dict_v01(multi.validate_multiroot_v01(outcome))


class JournalV01:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        require_v01(not self.directory.exists(), 'g40_output_exists')
        self.directory.mkdir(parents=True)
        self.times = {}

    def save(self, name, value):
        (self.directory / name).write_bytes(canonical_v01(value))

    @contextmanager
    def phase(self, name):
        start = time.monotonic()
        self.mark(name, 'START')
        try:
            yield
        except BaseException:
            self.mark(name, 'FAILED', time.monotonic() - start)
            raise
        else:
            self.times[name] = time.monotonic() - start
            self.mark(name, 'COMPLETE', self.times[name])

    def mark(self, name, state, seconds=None):
        row = dict(phase=name, state=state, wall_ns=str(time.time_ns()), elapsed_seconds=seconds)
        with (self.directory / 'phases.jsonl').open('ab') as f:
            f.write(canonical_v01(row) + b'\n')
        print(json.dumps(row), flush=True)


def preflight_v01(directory):
    journal = JournalV01(directory)
    controls = {}
    with journal.phase('setup'):
        fixture = fixture_v01(); config = fixture['controlled']
        claim_ns = time.time_ns(); now = claim_ns // 10**9
        invocation = 'g40:airline:' + str(claim_ns)
        constraints, snapshot, selection, selected, reports = controlled_source_v01(config, now, invocation)
        semantic_ref = 'g40:semantic:' + invocation
        material = checks.material_v01(constraints, snapshot, selected.offer_id, semantic_ref)
        clock = hosts.TrustedWorkSourceSnapshotV01((), actions.build_logical_time_bridge_v01(origin_utc_epoch_seconds=now,
            seconds_per_tick=1, bridge_policy_version='g40.controlled'), now, 'g40.controlled_utc', invocation, 0)
        source = current_source_v01(invocation, clock, material)
        transaction = 'transaction:' + invocation
        env = dict(pt_created_at=utc_v01(now), kt_asof=utc_v01(now), et_observed_at=None, ct_session_anchor=invocation,
            ttl_seconds=900, freshness_class='static', valid_from=utc_v01(now), valid_to=utc_v01(now+900))
        policy_ref = 'g40:policy:' + digest_v01(constraints)
        prediction = dict(profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID, predicted=True, expected_fp=500000000,
            claim_wall_ns=str(claim_ns), dependencies_sha256=digest_v01(material), semantic_ref=semantic_ref,
            operation='AIRLINE_CONSTRAINT_CHECK', source_observation_refs=[material['checks'][0]['observations'][0]['observation_id']],
            policy_ref=policy_ref, valid_from=now, valid_to=now+900, sequence=1)
        claim = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='g34:prediction:' + digest_v01(prediction),
            artifact_type='SemanticEvidence', schema_version='v1', transaction_id=transaction, owner_root_id=ROOT,
            source_component='g40_prospective_source', authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED',
            payload=prediction, trace_refs=(semantic_ref,), parent_refs=(), time_envelope=env)
        journal.save('prospective.json', claim)
        journal.save('input.json', dict(fixture=fixture, constraints=constraints, snapshot=snapshot, selection=selection,
            selected=selected, selection_rule='LOWER_PRICE_EXISTING_CLIENT_PREFERENCE_NOT_GT', validation=reports, material=material, source=source))
    with journal.phase('admission_and_policy'):
        catalogue = catalogue_v01()
        constraint_definition = next(a for a in catalogue if a.definition.operation_id == 'atlas.airline.constraint')
        provenance_definition = next(a for a in catalogue if a.definition.operation_id == 'g40.airline.provenance')
        proposal = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='g40:proposal:' + digest_v01(material),
            artifact_type='SemanticArchitectProposal', schema_version='v1', transaction_id=transaction, owner_root_id=ROOT,
            source_component='semantic_architect', authority_class='ADVISORY', lifecycle_state='PROPOSED',
            payload=dict(material=material, profile=PROFILE), trace_refs=('g40:intent:' + invocation,),
            parent_refs=(source.bsep_packet['packet_id'], claim.artifact_id), time_envelope=env)
        literal = work.WorkLiteralV01(actions.ActionEffectParameterRecordV01('material', 'TEXT', canonical_v01(material).decode()))
        item = work.WorkItemV01('constraint', constraint_definition.definition.definition_id, ROOT,
            (work.WorkInputBindingV01('material', literal),), (), (), None, None)
        common = dict(catalogue=catalogue, source_context=source, semantic_proposal=proposal)
        candidate = work.build_work_program_candidate_v01(task_id=invocation, previous_revision_id=None,
            intent_ref='g40:intent:' + invocation, bsep_ref=source.bsep_packet['packet_id'], semantic_proposal_ref=proposal.artifact_id,
            catalogue_revision=0, budget=work.WorkBudgetV01(*(config[k] for k in
                ('max_items', 'max_children', 'max_model_calls', 'max_compute_units', 'max_revisions'))),
            items=(item,), trigger_evidence_refs=(), **common)
        policy = work.build_work_task_policy_v01(candidate, **common, host_instance_ref='host:' + ROOT,
            definition_ids=tuple(sorted(a.definition.definition_id for a in catalogue)), resource_refs=())
        require_v01(work.validate_installed_work_task_policy_v01(policy, owning_root_id=ROOT, catalogue=catalogue), 'g40_policy')
        class Source:
            reads = 0
            def read_current_v01(self):
                self.reads += 1
                return clock
        trusted = Source()
        host = hosts.build_root_work_execution_host_v01(owning_root_id=ROOT, registry=actions.build_empty_action_commit_packet_registry_v02(),
            catalogue=catalogue, packet_bindings=(), current_dependency_observations=(), logical_time_bridge=clock.logical_time_bridge,
            trusted_source=trusted, task_policies=(policy,))
        journal.save('policy.json', policy)
        journal.save('admissions.json', tuple(firewall.snapshot_admitted_capability_v01(a) for a in catalogue))
    with journal.phase('materialization_and_enrollment'):
        program = work.materialize_work_program_v01(candidate, **common)
        context = work.enroll_work_program_v01(host, program, **common, expected_revision=host.state_revision)
        journal.save('before.json', work.inspect_work_task_v01(host, task_id=invocation))
    with journal.phase('constraint_dispatch'):
        outcome = work.advance_work_program_v01(program, **common, host_map={ROOT:host}, continuation_context=context)
        results = outcome.results
        require_v01(outcome.status == 'COMPLETED', 'g40_constraint_not_completed')
        event_ns = time.time_ns()
        artifact = work.work_program_result_to_artifact_v01(program, results, **common, host_map={ROOT:host})
        journal.save('constraint_result.json', dict(program=program, results=results, artifact=artifact, snapshot=outcome.snapshot))
    with journal.phase('continuation_and_provenance_dispatch'):
        try:
            work.advance_work_program_v01(program, **common, host_map={ROOT:host}, results=results, continuation_context=context)
        except ValueError as error:
            controls['stale_context'] = str(error)
        else:
            raise AssertionError('g40_stale_context_accepted')
        context = work.work_continuation_context_v01(host, task_id=invocation, expected_revision=host.state_revision)
        trigger = work.build_work_revision_trigger_v01(context, work_id='constraint', output_field='material')
        second = work.WorkItemV01('provenance', provenance_definition.definition.definition_id, ROOT,
            (work.WorkInputBindingV01('material', literal), work.WorkInputBindingV01('previous', trigger.output)), (), (), None, None)
        revision = work.revise_work_program_v01(context, previous_revision_id=candidate.revision_id, trigger=trigger,
            items=(second,), budget=work.WorkBudgetV01(4,0,0,3,0), **common)
        context2 = work.work_continuation_context_v01(host, task_id=invocation, expected_revision=host.state_revision)
        second_common = dict(common, continuation_context=context2)
        final = work.advance_work_program_v01(revision.program, **second_common, host_map={ROOT:host})
        require_v01(final.status == 'COMPLETED', 'g40_provenance_not_completed')
        artifact2 = work.work_program_result_to_artifact_v01(final.program, final.results, **second_common, host_map={ROOT:host})
        journal.save('provenance_result.json', dict(program=final.program, results=final.results, artifact=artifact2,
            snapshot=final.snapshot, trigger=trigger))
        fresh = work.work_continuation_context_v01(host, task_id=invocation, expected_revision=host.state_revision)
        retry = work.advance_work_program_v01(final.program, **dict(common, continuation_context=fresh),
            results=final.results, host_map={ROOT:host})
        require_v01(retry.snapshot == final.snapshot and retry.results == final.results, 'g40_terminal_retry')
        controls['terminal_retry_unchanged'] = True
        require_v01(final.snapshot.usage.compute_units == 2 and final.snapshot.policy == policy, 'g40_cumulative_spending')
        output = json.loads(results[0].result.output[0].value)
        provenance = json.loads(final.results[0].result.output[0].value)
        live = dict(host=host, material=canonical_v01(material), output=output, provenance=provenance,
            artifact=artifact, provenance_artifact=artifact2, source=source, semantic_ref=semantic_ref,
            programs=((program, results, common), (final.program, final.results, second_common)))
    with journal.phase('contextual_controls_and_root_consumption'):
        other = next(r for r in snapshot.authoritative_offer_records if r.offer_id != selected.offer_id)
        altered = replace(snapshot, authoritative_offer_records=tuple(replace(r, amount=r.amount+1) for r in snapshot.authoritative_offer_records))
        altered = replace(altered, candidate_set_digest=binding.compute_airline_candidate_set_digest_v01(altered))
        require_v01(binding.validate_airline_candidate_snapshot_v01(altered).validation_status == 'PASS', 'g40_coherent_source_control')
        for name, target, offer in (('wrong_offer', snapshot, other.offer_id), ('coherent_wrong_source', altered, selected.offer_id)):
            try:
                consume_v01(live, constraints=constraints, snapshot=target, selected_offer_id=offer)
            except ValueError as error:
                controls[name] = dict(reason=str(error), valid_source=plain_v01(target), offer_id=offer)
            else:
                raise AssertionError('g40_negative_accepted:' + name)
        controls['positive_neighbor'] = consume_v01(live, constraints=constraints, snapshot=snapshot, selected_offer_id=selected.offer_id) == material
        reviews = {}; inputs = {}; consents = {}
        for root in ROOTS:
            consent = None if root == binding.AIRLINE_ROOT_ID else dict(root_id=root, offer_id=selected.offer_id,
                source_digest=snapshot.candidate_set_digest, max_amount=config['max_amount'], currency=selected.currency, purpose='PREPARATION_ONLY')
            consents[root] = consent
            reviews[root], inputs[root] = review_v01(live, root=root, constraints=constraints, snapshot=snapshot, selected=selected,
                consent=consent, bank_limit=config['bank_limit'], now=int(time.time()))
        require_v01(all(r[2].decision == 'ACCEPT' for r in reviews.values()), 'g40_positive_roots')
        refusal, refusal_input = review_v01(live, root=binding.BANK_ROOT_ID, constraints=constraints, snapshot=snapshot,
            selected=selected, consent=None, bank_limit=config['bank_limit'], now=int(time.time()))
        require_v01(refusal[2].decision == 'NEEDS_USER', 'g40_missing_bank_consent')
        mixed = dict(reviews); mixed[binding.BANK_ROOT_ID] = refusal
        positive, positive_validation = multiroot_v01(reviews, selected.offer_id)
        contrast, contrast_validation = multiroot_v01(mixed, selected.offer_id)
        journal.save('roots.json', dict(reviews=reviews, inputs=inputs, consents=consents,
            refusal=refusal, refusal_input=refusal_input, positive=positive, positive_validation=positive_validation,
            mixed=contrast, mixed_validation=contrast_validation))
        # Preparation only: no corridor, action installation or dispatch follows.
        hold = binding.build_hold_packet_for_offer_v01(snapshot, selected.offer_id)
        require_v01(hold.offer_id == selected.offer_id and hold.amount == selected.amount, 'g40_hold_preparation')
        journal.save('hold_preparation.json', dict(status='PREPARATION_ONLY_NOT_EXECUTED', hold=hold,
            consumed_root_refs=[r[2].decision_id for r in reviews.values()], source_digest=snapshot.candidate_set_digest))
    with journal.phase('native_g3_proof'):
        capture_ns = time.time_ns()
        closure = {Path(module.__file__).name: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
            for module in (checks, binding, hosts, work, roots, semantic, abi, feedback, history, calibration)}
        closure[Path(__file__).name] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        context_native = dict(source_id='g40:context:' + digest_v01(material), local_root_scope_id=ROOT, domain='AIRLINE',
            pack_family_id='REVOCABLE_ACTION', advisory_source_class='G40_CONTROLLED_CONSTRAINT_PREDICTION',
            advisory_source_revision=closure[Path(__file__).name], advice_claim_profile_id=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
            route_family_id='PURE_AIRLINE_CONSTRAINT', task_risk_class='INFORMATIONAL',
            validation_profile_id='G34_TYPED_BOOLEAN_COMPLETED_WORK_V01', policy_semantics_version=policy_ref,
            history_key_profile_id='G3_TYPED_HISTORY_KEY_V01', task_class_id='AIRLINE_CONSTRAINT_CHECK',
            capability_contract_version='atlas.airline.constraint.v01', transaction_id=transaction,
            run_id=invocation, episode_id=invocation, scenario_id=config['scenario_id'])
        operation = dict(operation='AIRLINE_CONSTRAINT_CHECK', object_id=selected.offer_id, recipient=ROOT)
        occurrence = 'g40:occurrence:' + digest_v01(prediction); capture = 'g40:capture:' + digest_v01(artifact)
        native = dict(source_profile_id=feedback.NATIVE_SOURCE_PROFILE_ID, evidence_class='NATIVE_CONTROLLED_OBSERVATION',
            context=context_native, policy=dict(source_id=policy_ref, revision=policy_ref, **operation),
            origin=dict(source_id='g40:origin:' + invocation, occurrence_id=occurrence),
            proposal=dict(source_id=semantic_ref, origin_ref='g40:origin:' + invocation, created_at=now, recommendation='PROCEED', **operation),
            expectation=dict(source_id=claim.artifact_id, created_at=now, expected_fp=prediction['expected_fp']),
            observation=dict(source_id=capture, proposal_ref=semantic_ref, occurrence_ref=occurrence, **operation,
                result_revision=context_native['capability_contract_version'], event_time=event_ns//10**9,
                boundary_disposition='PERMITTED', effect_count=0, result_state='PRESENT', failure='NONE'),
            closure=dict(source_id='g40:closure:' + digest_v01(closure), sources=closure),
            native=dict(claim_wall_ns=str(claim_ns), event_wall_ns=str(event_ns), capture_wall_ns=str(capture_ns),
                elapsed_ns=event_ns-claim_ns, sequence=1, root_decision_ref=reviews[ROOT][2].decision_id,
                plan_artifact_ref=program.topology_artifact.artifact_id, result_artifact_ref=artifact.artifact_id,
                material_sha256=digest_v01(material), output_sha256=digest_v01(output), work_count=1,
                reached_boundary='WORK_ROOT', reason=None, time_envelope=plain_v01(artifact)['time_envelope'],
                capture_ref=capture, semantic_ref=semantic_ref, dependencies_sha256=digest_v01(material)))
        journal.save('native_g3_input.json', native)
        source_native = feedback.NativeOutcomeSourceContextV01(canonical_v01(native))
        proof = history.NativeOutcomeWorkProofV01(source_native, host, program, results, common, (), canonical_v01(material), reviews[ROOT])
        history.validate_native_work_proof_v01(proof)
        predictive = feedback.PredictiveOutcomeSourceContextV01(canonical_v01(dict(profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
            native_source=native, claim_artifact=plain_v01(claim), result_artifact=plain_v01(artifact))))
        timestamp = int(time.time())
        observation = feedback.build_outcome_observation_v01(source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
            explicit_times=dict(ingested_time=timestamp, evaluated_at=timestamp, timestamp=timestamp))
        ofe = feedback.build_outcome_feedback_v01(observation=observation, source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
        reasons = feedback.validate_outcome_feedback_against_sources_v01(ofe, source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
        require_v01(not reasons, 'g40_supplied_feedback:' + repr(reasons))
        event = calibration.bind_outcome_feedback_event_v01(ofe, source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
        journal.save('g3.json', dict(native=native, predictive=json.loads(predictive.canonical), observation=json.loads(observation.canonical),
            feedback=json.loads(ofe.canonical), event=dict(source_profile_id=event.source_profile_id,
                feedback_canonical=json.loads(event.feedback_canonical), source_canonical=json.loads(event.source_canonical)),
            live_proof_validation='PASS', supplied_reasons=reasons,
            history_record_query_current_descent='NOT_RUN_MAPPED_ONLY', prospective_file_sha256=hashlib.sha256((journal.directory/'prospective.json').read_bytes()).hexdigest()))
    journal.save('controls.json', controls)
    journal.save('after.json', work.inspect_work_task_v01(host, task_id=invocation))
    journal.save('attempts.json', host.work_attempts)
    summary = dict(result='G40_NATIVE_PREFLIGHT_COMPLETE_FOR_INDEPENDENT_REVIEW', source_admission='UNADMITTED_PENDING_INDEPENDENT_REVIEW',
        phase_seconds=journal.times, work_dispatches=len(host.work_attempts), compute_units=final.snapshot.usage.compute_units,
        original_compute_cap=policy.max_compute_units, revisions=final.snapshot.usage.revisions,
        mandatory_remaining_dispatches=0, unspent_compute_units=policy.max_compute_units-final.snapshot.usage.compute_units,
        model_calls=0, provider_calls=0, business_effects=0, trusted_source_reads=trusted.reads,
        root_decisions={k:v[2].decision for k,v in reviews.items()}, bank_missing_consent=refusal[2].decision,
        mixed_status=contrast['outcome_status'], native_proof='PASS', predictive_source='PASS', history_loop='NOT_RUN',
        adaptive_allocation='NOT_IMPLEMENTED', full_gate4='NOT_CLAIMED')
    journal.save('summary.json', summary)
    return summary


# G42 is additive: the reviewed G40 entry above retains its original behavior.
def native_config_v42():
    return json.loads((Path(__file__).resolve().parents[3]/'fixtures/gate4_reference_native_v01.json').read_bytes())


def native_domain_v42(constraints, snapshot):
    selection=binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(),constraints,snapshot)
    reports=(binding.validate_airline_candidate_snapshot_v01(snapshot),binding.validate_client_root_travel_constraint_set_v01(constraints),
        binding.validate_airline_semantic_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(),constraints,snapshot,selection))
    require_v01(all(r.validation_status=='PASS' for r in reports),'g42_original_domain')
    return dict(constraints=feedback.g35_record_to_plain_v01(constraints),snapshot=feedback.g35_record_to_plain_v01(snapshot),
        selection=feedback.g35_record_to_plain_v01(selection))


def validate_native_domain_v42(domain):
    require_v01(set(domain)=={'constraints','snapshot','selection'},'g42_domain_shape')
    constraints=feedback.g35_record_from_plain_v01(domain['constraints'])
    snapshot=feedback.g35_record_from_plain_v01(domain['snapshot'])
    require_v01(native_domain_v42(constraints,snapshot)==domain,'g42_domain_source_binding')
    return constraints,snapshot


def quantum_result_v42(material):
    require_v01(set(material)=={'domain','branch','ordinal','field','offer_id'},'g42_quantum_shape')
    constraints,snapshot=validate_native_domain_v42(material['domain'])
    order=('route','baggage','seat','price','inventory','change_terms')
    ordinal=material['ordinal']; require_v01(type(ordinal) is int and 1<=ordinal<=6 and material['field']==order[ordinal-1],'g42_quantum_ordinal')
    record=next((r for r in snapshot.authoritative_offer_records if r.offer_id==material['offer_id']),None)
    require_v01(record is not None,'g42_quantum_offer')
    actual={'route':[record.route_ref,record.departure_date,record.return_date],
        'baggage':record.baggage_included,'seat':list(record.seat_characteristics),
        'price':[record.amount,record.currency],'inventory':[record.inventory_available,record.airline_policy_valid],
        'change_terms':[record.changeable,record.change_penalty_class]}[material['field']]
    selection=binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(),constraints,snapshot)
    return dict(stage='RESULT',branch=material['branch'],ordinal=ordinal,field=material['field'],offer_id=record.offer_id,
        checked_value=actual,hard_compatible=record.offer_id in selection.client_hard_compatible_candidate_ids,
        source_digest=snapshot.candidate_set_digest,input_sha256=digest_v01(material))


def strategy_work_result_v42(values):
    from hedgehog.gate4_strategy_reference_v01 import evaluate_reference_strategy_v01
    from hedgehog.gate4_reference_contracts_v01 import ReferenceValueV01
    material=values['material']; validate_native_domain_v42(material['domain'])
    require_v01(values['previous']==checks.evaluate_v01(material['initial_material']),'g42_actual_historical_constraint')
    consumed=[]
    for key in sorted(k for k in values if k.startswith('q')):
        output=values[key]
        candidates=[m for m in material['quanta'] if m['branch']==output['branch'] and m['ordinal']==output['ordinal']]
        require_v01(len(candidates)==1,'g42_quantum_not_declared')
        expected=quantum_result_v42(dict(candidates[0],domain=material['domain']))
        require_v01(output==expected,'g42_actual_quantum_consumption')
        consumed.append(output)
    require_v01(len({(o['branch'],o['ordinal']) for o in consumed})==len(consumed),'g42_duplicate_quantum')
    proof=values['allocation_proof']
    validate_allocation_proof_v43(proof,material,consumed)
    report=evaluate_reference_strategy_v01(material['strategy_inputs'],independently_bound_context=material['independent_context'])
    return dict(stage='RESULT',input_sha256=digest_v01(material),strategy_report=report.plain(),strategy_identity=report.identity,
        consumed_quanta=consumed,consumed_previous_sha256=digest_v01(values['previous']),domain_sha256=digest_v01(material['domain']),
        allocation_identity=ReferenceValueV01('allocation_report',proof['allocation']).identity,allocation_proof_sha256=digest_v01(proof),original_basis_sha256=digest_v01(proof['basis']))


def native_input_validator_v42(definition, inputs):
    errors=firewall.validate_capability_values_v01(definition.input_fields,inputs)
    if not errors:
        try:
            values={v.parameter_name:json.loads(v.value) for v in inputs}
            if definition.operation_id=='g42.airline.quantum': quantum_result_v42(values['material'])
            else: strategy_work_result_v42(values)
        except (ValueError,TypeError,KeyError) as exc: errors=('g42_native_input:'+str(exc),)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=inputs,invocation_id=None,valid=not errors,reason_codes=errors)


def execute_quantum_v42(invocation):
    result=quantum_result_v42(json.loads(invocation.inputs[0].value))
    return (actions.ActionEffectParameterRecordV01('material','TEXT',canonical_v01(result).decode()),)


def execute_strategy_v42(invocation):
    result=strategy_work_result_v42({v.parameter_name:json.loads(v.value) for v in invocation.inputs})
    return (actions.ActionEffectParameterRecordV01('material','TEXT',canonical_v01(result).decode()),)


def native_output_validator_v42(definition, invocation, output):
    errors=firewall.validate_capability_values_v01(definition.output_fields,output)
    if not errors:
        values={v.parameter_name:json.loads(v.value) for v in invocation.inputs}
        expected=quantum_result_v42(values['material']) if definition.operation_id=='g42.airline.quantum' else strategy_work_result_v42(values)
        if json.loads(output[0].value)!=expected: errors=('g42_native_output',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)


def native_catalogue_v42():
    entries=[a for a in checks.catalogue_v01() if a.definition.operation_id=='atlas.airline.constraint']
    for name,executor in (('quantum',execute_quantum_v42),('strategy',execute_strategy_v42)):
        functions=(native_input_validator_v42,native_output_validator_v42,executor)
        codes=tuple(hosts.observe_local_capability_code_v01(f) for f in functions)
        field=lambda n,required:firewall.build_capability_field_v01(name=n,value_type='TEXT',required=required,consequential=False)
        inputs=(field('material',True),) if name=='quantum' else (field('material',True),field('allocation_proof',True),field('previous',True))+tuple(field('q'+str(i),False) for i in range(12))
        definition=firewall.build_capability_definition_v01(operation_id='g42.airline.'+name,version='v01',effect_kind='PURE',business_semantics=None,
            input_fields=inputs,output_fields=(field('material',True),),resource_refs=(),input_validator_ref=codes[0].public_symbol,
            output_validator_ref=codes[1].public_symbol,executor_ref=codes[2].public_symbol,code_sha256s=tuple((c.public_symbol,c.source_sha256) for c in codes))
        entries.append(hosts.admit_local_capability_v01(definition=definition,input_validator=functions[0],output_validator=functions[1],executor=functions[2],
            catalogue_revision=0,host_instance_ref='host:'+ROOT))
    return tuple(entries)


def native_basis_v42(live):
    from hedgehog.gate4_reference_runtime_v01 import local_id_v01
    snapshot=work.inspect_work_task_v01(live['host'],task_id=live['task_id'])
    mapping=[]
    for kind,values in [('root',ROOTS),('offer',tuple(r.offer_id for r in live['snapshot'].authoritative_offer_records)),
        ('task',(live['task_id'],)),('transaction',(live['proposal'].transaction_id,)),('bsep',(live['source'].bsep_packet['packet_id'],)),
        ('intent',(live['policy'].intent_ref,)),('policy',(live['policy'].source_ref,)),
        ('definition',tuple(a.definition.definition_id for a in live['catalogue']))]:
        mapping.extend(dict(kind=kind,local_id=local_id_v01(kind,v),native_id=v) for v in values)
    require_v01(len({r['local_id'] for r in mapping})==len(mapping),'g42_one_to_one_ids')
    return dict(profile='G42_ORIGINAL_AND_PROJECTION_BINDING_V01',domain=native_domain_v42(live['constraints'],live['snapshot']),
        policy=plain_v01(live['policy']),usage=plain_v01(snapshot),source=plain_v01(live['source']),
        time_envelope=plain_v01(live['proposal'])['time_envelope'],configuration=live['config'],utility_profile=live['profile'],
        mapping=mapping,host_sources=plain_v01(live['host'].current_sources),
        history=live['history_evidence_binding'],definition_roles=plain_v01(live['proposal'])['payload']['definition_roles'])


def native_math_context_v42(live,basis):
    from hedgehog.gate4_reference_contracts_v01 import G4_REFERENCE_NUMERIC_V01, NUMERIC_HASH, UTILITY_HASH, digest
    from hedgehog.gate4_reference_runtime_v01 import local_id_v01 as lid
    ctx=dict(profile=G4_REFERENCE_NUMERIC_V01,scope=PROFILE,schema='g4_reference:v01',evaluation_id=lid('evaluation',digest_v01(basis)),
        domain_id='g4_reference:airline',owner_root_id=lid('root',ROOT),task_id=lid('task',live['task_id']),
        transaction_id=lid('transaction',live['proposal'].transaction_id),intent_ref=lid('intent',live['policy'].intent_ref),
        bsep_ref=lid('bsep',live['source'].bsep_packet['packet_id']),participants=sorted(lid('root',r) for r in ROOTS),
        evaluation_time=live['clock'].evaluation_time,time_envelope_ref=lid('time',digest_v01(basis['time_envelope'])),
        source_snapshot_ref=lid('projection',digest_v01(basis)),source_snapshot_hash='0'*64,
        candidate_set_ref=lid('candidate_set',live['snapshot'].candidate_set_snapshot_id),candidate_set_hash='0'*64,
        policy_ref=lid('policy',live['policy'].source_ref),policy_hash='0'*64,
        utility_profile_ref='g4_reference:utility:v01',utility_profile_hash=UTILITY_HASH,
        numeric_profile_ref='g4_reference:numeric:v01',numeric_profile_hash=NUMERIC_HASH,
        dependencies=[lid('native_snapshot',live['snapshot'].candidate_set_digest)],catalogue_revision='g4_reference:catalogue:0',
        origin='NATIVE_SOURCE_BOUND_G42_V01',dispositions=[dict(id='g4_reference:source',state='KNOWN',source_ref=lid('original',digest_v01(basis['domain'])))],
        native_binding=dict(profile='G42_ORIGINAL_AND_PROJECTION_BINDING_V01',basis_sha256=digest_v01(basis),
            original_snapshot_sha256=digest_v01(basis['domain']['snapshot']),original_policy_sha256=digest_v01(basis['policy']),
            original_usage_sha256=digest_v01(basis['usage']),original_envelope_sha256=digest_v01(basis['time_envelope']),id_mapping_sha256=digest_v01(basis['mapping'])))
    ctx['policy_hash']=digest(dict(total=live['policy'].max_compute_units,policy_ref=ctx['policy_ref'],owner_root_id=ctx['owner_root_id'],task_id=ctx['task_id']))
    return ctx


def derive_strategy_v42(live,basis):
    from hedgehog.gate4_reference_contracts_v01 import Q, G4_REFERENCE_NUMERIC_V01, checked, digest
    from hedgehog.gate4_reference_runtime_v01 import local_id_v01 as lid
    from hedgehog.outcome_calibration_v01 import round_half_even_rational_v01 as rhe
    ctx=native_math_context_v42(live,basis); config=live['config']; profile=config['utility_profiles'][live['profile']]
    candidates=[]
    for record in live['snapshot'].authoritative_offer_records:
        cid=lid('offer',record.offer_id); utilities=[]; refs=[]
        for root in ROOTS:
            if root==ROOT:
                features=[('price',rhe((live['constraints'].max_amount-record.amount)*Q,config['normalization']['client_margin_denominator']),profile['client_price_weight']),
                    ('seat',Q if 'extra_legroom' in record.seat_characteristics else 0,profile['client_extra_legroom_weight'])]
            elif root==binding.AIRLINE_ROOT_ID: features=[('revenue',rhe(record.amount*Q,config['normalization']['revenue_denominator']),Q)]
            else: features=[('budget_margin',rhe((config['bank_limit']-record.amount)*Q,config['normalization']['bank_margin_denominator']),Q)]
            terms=[]
            for name,value,weight in features:
                ref=lid('feature',record.offer_id+root+name); refs.append(ref)
                terms.append(dict(id=lid('term',root+name),feature_fp=value,weight_fp=weight,source_ref=ref,interpretation='Prospective '+name+' normalization from exact native offer and local configuration'))
            utilities.append(dict(root_id=lid('root',root),issuer_ref=lid('root',root),role_ref=lid('role',root),candidate_id=cid,
                source_ref=lid('utility',record.offer_id+root+live['profile']),profile=G4_REFERENCE_NUMERIC_V01,version=1,unit='FIXED_POINT_Q',
                validity='CURRENT',uncertainty='DISCLOSED',terms=terms,penalties=dict(risk=0,latency=0,coordination=0)))
        selection=binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(),live['constraints'],live['snapshot'])
        c=dict(id=cid,source_ref=lid('native_offer',record.offer_id),source_hash='0'*64,participants=ctx['participants'],feature_refs=sorted(refs),
            required_roots=ctx['participants'],hard=[dict(id='g4_reference:hard:compatible',state='TRUE' if record.offer_id in selection.client_hard_compatible_candidate_ids else 'FALSE',evidence_ref=lid('selection',selection.selection_input_id))],
            policy_ref=ctx['policy_ref'],time_envelope_ref=ctx['time_envelope_ref'],capability_ref=lid('definition',live['definitions']['g42.airline.strategy']),
            no_deal_ref='g4_reference:no_deal:configured',utilities=utilities)
        c=checked('candidate',c); c['source_hash']=digest({k:v for k,v in c.items() if k!='source_hash'}); candidates.append(c)
    ds=[dict(root_id=r,source_ref=lid('disagreement',r),validity='CURRENT',value=config['disagreement_fp']) for r in ctx['participants']]
    data=checked('strategy_input',dict(context=ctx,candidates=candidates,disagreements=ds))
    data['context']['candidate_set_hash']=digest(data['candidates'])
    data['context']['source_snapshot_hash']=digest(dict(candidates=data['candidates'],disagreements=data['disagreements']))
    return data


def derive_budget_v42(live,basis,final_material):
    from copy import deepcopy
    from hedgehog.gate4_reference_contracts_v01 import checked, digest
    from hedgehog.gate4_reference_runtime_v01 import local_id_v01 as lid
    ctx=native_math_context_v42(live,basis); branches=[]
    selection=binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(),live['constraints'],live['snapshot'])
    for b in live['config']['branches']:
        offer=live['snapshot'].authoritative_offer_records[b['offer_index']]
        branch=dict(id=lid('branch',b['id']),material_ref=lid('branch_material',b['id']+digest_v01(basis['domain'])),catalogue_revision=ctx['catalogue_revision'],
            hard=[dict(id='g4_reference:hard:current',state='TRUE' if offer.offer_id in selection.client_hard_compatible_candidate_ids else 'FALSE',evidence_ref=ctx['dependencies'][0])],
            eligible='TRUE' if offer.airline_policy_valid and not offer.expired else 'FALSE',available='TRUE' if offer.inventory_available else 'FALSE',lower=b['lower'],upper=b['upper'])
        for key in ('relevance','lineage','uncertainty','cost'):
            branch[key]=dict(value=b[key],source_ref=lid('configured_feature',b['id']+key+digest_v01(live['config'])),normalization='FIXED_Q_0_1',interpretation=live['config']['feature_interpretation'])
        used=b['id']==live['config']['comparison']['history_branch'] and live['opened'] is not None
        branch['prior']=dict(value=live['opened']['prior']['prior_fp'] if used else 0,source_ref=lid('history',live['opened']['bridge'].artifact_id if used else b['id']+':cold'),
            disposition='USABLE' if used else 'ABSENT',normalization='FIXED_Q_SIGNED',interpretation='Raw source-bound G3 prior once; cold only after current discovery')
        branches.append(branch)
    p=checked('pressure_input',dict(context=ctx,branches=branches)); p['context']['source_snapshot_hash']=digest(p['branches']);p['context']['candidate_set_hash']=digest([b['id'] for b in p['branches']])
    ctx=p['context']; snapshot=basis['usage']
    return checked('budget',dict(context=deepcopy(ctx),id=lid('budget',digest_v01(snapshot)),original_policy_ref=ctx['policy_ref'],original_policy_hash=ctx['policy_hash'],
        total=live['policy'].max_compute_units,spent=snapshot['usage']['compute_units'],host_revision=snapshot['host_revision'],
        spending_snapshot_ref=lid('spending',digest_v01(snapshot)),spending_snapshot_hash=digest(dict(spent=snapshot['usage']['compute_units'],host_revision=snapshot['host_revision'],
            owner_root_id=ctx['owner_root_id'],task_id=ctx['task_id'],transaction_id=ctx['transaction_id'])),
        mandatory=[dict(id='g4_reference:mandatory:strategy',count=1,kind='FINAL_CONSUMER',definition_ref=lid('definition',live['definitions']['g42.airline.strategy']),
            material_ref=lid('aggregate',digest_v01(final_material)),material_sha256=digest_v01(final_material),source_ref=lid('proposal',live['proposal'].artifact_id),catalogue_revision=ctx['catalogue_revision'])],
        pressure_inputs=p))


def projection_view_v43(basis,proposal):
    """Pure original-record view. Never creates a Host, permission or live source."""
    from types import SimpleNamespace
    constraints,snapshot=validate_native_domain_v42(basis['domain'])
    p=plain_v01(proposal);need=p['payload']
    for key,value in dict(domain=basis['domain'],finite_catalogue=basis['configuration'],utility_profile=basis['utility_profile'],history=basis['history'],definition_roles=basis['definition_roles']).items():
        require_v01(canonical_v01(need[key])==canonical_v01(value),'g43_proposal_original:'+key)
    require_v01(p['time_envelope']==basis['time_envelope'],'g43_original_envelope')
    mapping=basis['mapping']
    for row in mapping:
        from hedgehog.gate4_reference_runtime_v01 import local_id_v01
        require_v01(row['local_id']==local_id_v01(row['kind'],row['native_id']),'g43_original_id_mapping')
    definitions=basis['definition_roles']
    require_v01(set(definitions.values())=={r['native_id'] for r in mapping if r['kind']=='definition'},'g43_definition_mapping')
    opened=None
    if basis['history'].get('bridge'):
        b=basis['history']['bridge']
        opened=dict(prior=b['payload']['prior'],bridge=SimpleNamespace(artifact_id=b['artifact_id']))
    return dict(constraints=constraints,snapshot=snapshot,config=basis['configuration'],profile=basis['utility_profile'],
        task_id=basis['policy']['task_id'],policy=SimpleNamespace(**basis['policy']),proposal=SimpleNamespace(**p),
        clock=SimpleNamespace(**basis['host_sources']),source=SimpleNamespace(**basis['source']),definitions=definitions,opened=opened)


def derive_budget_from_originals_v43(basis,proposal,final_material):
    view=projection_view_v43(basis,proposal)
    expected=derive_strategy_v42(view,basis)
    require_v01(final_material['domain']==basis['domain'] and final_material['strategy_inputs']==expected
        and final_material['independent_context']==expected['context'],'g43_final_original_derivation')
    return derive_budget_v42(view,basis,final_material)


def validate_allocation_proof_v43(proof,material,consumed):
    from hedgehog.gate4_pressure_budget_v01 import validate_reference_allocation_v01
    require_v01(set(proof)=={'profile','basis','proposal','budget','allocation'} and proof['profile']=='G43_ALLOCATION_WORK_PROOF_V01','g43_allocation_proof_shape')
    expected=derive_budget_from_originals_v43(proof['basis'],proof['proposal'],material)
    require_v01(expected==proof['budget'],'g43_allocation_original_budget')
    report=validate_reference_allocation_v01(proof['allocation'],inputs=expected['pressure_inputs'],current_budget_context=expected).plain()
    require_v01(report['status']=='ALLOCATED','g43_allocation_proof_status')
    actual=sorted((o['branch'],o['ordinal']) for o in consumed)
    require_v01(actual==sorted((r['id'],i) for r in report['rows'] for i in range(1,r['allocation']+1)),'g43_actual_allocation_counts')
    return report


def validate_current_basis_v43(basis,now):
    """Current freshness is measured from original sources, never review age."""
    require_v01(type(now) is int,'g43_current_time_type')
    _,snapshot=validate_native_domain_v42(basis['domain'])
    second=lambda s:int(datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
    env=basis['time_envelope'];created=second(snapshot.snapshot_created_at)
    start=max(created,second(env['valid_from']),second(env['pt_created_at']),basis['host_sources']['evaluation_time'])
    end=min(created+snapshot.snapshot_ttl_seconds,second(env['valid_to']),second(env['pt_created_at'])+env['ttl_seconds'],
        *(created+r.ttl_seconds for r in snapshot.authoritative_offer_records))
    require_v01(start<=now<end and not snapshot.snapshot_expired and all(not r.expired for r in snapshot.authoritative_offer_records),'g43_current_source_expired_or_future')
    return dict(profile='G43_CURRENT_USE_V01',evaluation_time=now,valid_from=start,valid_to=end,
        task_id=basis['policy']['task_id'],basis_sha256=digest_v01(basis),source_clock=basis['host_sources'])


def current_use_v43(live):
    from hedgehog.gate4_reference_runtime_v01 import TaskClockV43
    require_v01(type(live['task_clock']) is TaskClockV43,'g43_trusted_task_clock')
    basis=live.get('basis') or native_basis_v42(live)
    result=validate_current_basis_v43(basis,live['task_clock'].now_v01(live['task_id']))
    live.setdefault('current_use_events',[]).append(result)
    return result


def reconstruct_allocation_basis_v43(*,host,task_id,common,history_store,task_clock):
    """Fixed trusted factory derives only from public enrollment and source originals."""
    need=plain_v01(common['semantic_proposal'])['payload']
    constraints,snapshot=validate_native_domain_v42(need['domain'])
    state=work.inspect_work_task_v01(host,task_id=task_id)
    require_v01(state.policy.task_id==task_id and host.owning_root_id==ROOT,'g43_enrolled_task')
    require_v01(state.policy.source_ref==work._source_ref(common['source_context'],common['semantic_proposal']),'g43_installed_original_source')
    live=dict(host=host,task_id=task_id,common=common,proposal=common['semantic_proposal'],source=common['source_context'],
        catalogue=common['catalogue'],policy=state.policy,constraints=constraints,snapshot=snapshot,config=need['finite_catalogue'],
        profile=need['utility_profile'],history_evidence_binding=need['history'],clock=host.current_sources)
    basis=native_basis_v42(live)
    validate_current_basis_v43(basis,task_clock.now_v01(task_id))
    require_v01(type(history_store) is history.OutcomeHistoryV01,'g43_actual_history_store')
    from .gate4_reference_history_v01 import keys_v01
    _,key,_=keys_v01(need['finite_catalogue'],constraints)
    opened,evidence=history_store.current_v01(history_key=key,root=ROOT,transaction=common['semantic_proposal'].transaction_id,
        evaluation_time=host.current_sources.evaluation_time)
    require_v01(canonical_v01(evidence.get('bridge'))==canonical_v01(need['history'].get('bridge')),'g43_enrolled_history_source')
    if opened is not None:
        now=task_clock.now_v01(task_id)
        require_v01(now<int(datetime.fromisoformat(plain_v01(opened['bridge'])['time_envelope']['valid_to']).timestamp()),'g43_current_history_expired')
        history_store.validate_opened_v01(opened,bridge=opened['bridge'],evaluation_time=opened['evaluation_time'])
    return basis


def local_review_v42(live,*,root,candidates,selected,scores,artifact,program,consent,informational=False,evaluation_time=None):
    """Ordinary Root, with independently checked source, local policy and consent."""
    current=current_use_v43(live)['evaluation_time']
    now=current if evaluation_time is None else evaluation_time
    require_v01(live['clock'].evaluation_time<=now<=current,'g43_review_future_or_unrelated')
    validate_native_domain_v42(native_domain_v42(live['constraints'],live['snapshot']))
    selection=binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(),live['constraints'],live['snapshot'])
    records={r.offer_id:r for r in live['snapshot'].authoritative_offer_records}
    subject=live['initial_material']['checks'][0]['offer_id'] if informational else next(
        row['native_id'] for row in live['basis']['mapping'] if row['kind']=='offer' and row['local_id']==selected)
    record=records[subject]; created=int(datetime.fromisoformat(live['snapshot'].snapshot_created_at).timestamp())
    fresh=created<=now<created+min(record.ttl_seconds,live['snapshot'].snapshot_ttl_seconds)
    local=dict(root=root,subject=subject,source=live['snapshot'].candidate_set_digest,terms=plain_v01(record),
        constraint=plain_v01(live['constraints']),consent=consent,now=now,producer=plain_v01(artifact),
        current_work_transaction=live['transaction'],purpose='INFORMATIONAL_CHECK' if informational else 'PREPARATION_ONLY')
    local_ref='g42:current_use:'+digest_v01(local); refs=(artifact.artifact_id,local_ref,live['snapshot'].candidate_set_snapshot_id)
    actor='g42:validator:'+root
    request=semantic.build_semantic_work_request_v01(request_id='g42:review:'+digest_v01(local),transaction_id=live['transaction'],
        target_root_id=root,runtime_topology_ref=program.topology_artifact.artifact_id,bounded_context_refs=refs,
        permitted_actor_ids=(actor,),permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=tuple(sorted(candidates)),
        required_evidence_classes=('DEPENDENCY_EVIDENCE',),forbidden_claims=('authority_creation',))
    evidence=tuple(semantic.build_evidence_binding_v01(evidence_id='binding:'+ref,evidence_ref=ref,
        evidence_class='DEPENDENCY_EVIDENCE',source_component_id=actor,provenance_ref=artifact.artifact_id,evidence_state='PRESENT') for ref in refs)
    claims=tuple(semantic.build_normalized_claim_v01(claim_id=key,subject=key,predicate='g42_checked_native_preparation',
        object_or_value=value,time_envelope_ref='g42:time:'+str(now),provenance_refs=refs,evidence_refs=tuple(e.evidence_id for e in evidence),
        confidence_micros=1000000,source_role='deterministic_runtime',source_mode='DETERMINISTIC') for key,value in sorted(candidates.items()))
    contribution=semantic.build_actor_contribution_v01(contribution_id='g42:contribution:'+digest_v01(local),request_id=request.request_id,
        actor_id=actor,actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref=live['source'].bsep_packet['packet_id'],
        scope=subject,bounded_context_refs=refs,claims=claims,evidence_bindings=evidence,constraint_bindings=(),uncertainty_bindings=(),
        requested_validators=('g42:independent_native_consumption',),forbidden_claims_observed=())
    packet=semantic.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),trust_profiles=trust.build_default_component_trust_profiles_v01())
    policies={ROOT:subject in selection.client_hard_compatible_candidate_ids,
        binding.AIRLINE_ROOT_ID:record.inventory_available and record.airline_policy_valid,
        binding.BANK_ROOT_ID:record.amount<=live['config']['bank_limit'] and record.currency==live['constraints'].currency}
    required=not informational and root in (ROOT,binding.BANK_ROOT_ID)
    scoped=consent is None or (consent['root_id']==root and consent['offer_id']==subject and consent['source_digest']==live['snapshot'].candidate_set_digest
        and record.amount<=consent['max_amount'] and consent['currency']==record.currency and consent['purpose']=='PREPARATION_ONLY')
    kernel=roots.build_root_decision_kernel_v01()
    decision_input=roots.build_root_decision_input_v01(transaction_id=live['transaction'],target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=local_ref,post_vv_passed=bool(candidates),validated_candidate_ids=sorted(candidates),rejected_candidate_ids=[],
            required_evidence_refs=list(refs),provided_evidence_refs=list(refs),hard_failure_reasons=[]),
        gt_advisory=dict(advisory_id='g42:advisory:'+digest_v01(dict(candidates=candidates,scores=scores)),candidate_ids=sorted(candidates),
            selected_candidate_id=selected,score_micros_by_candidate=scores,source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',
            actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id='g42:local:'+root,identity_passed=root in ROOTS,scope_passed=subject in records,
            hard_policy_passed=policies[root],allow_accept=policies[root],conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=required,user_permission_present=consent is not None,permission_scope_valid=scoped,
            permission_ref='g42:consent:'+digest_v01(consent) if consent else None),
        temporal_state=dict(temporal_valid=fresh,expired=not fresh or record.expired or live['snapshot'].snapshot_expired,
            not_before_satisfied=now>=created,time_envelope_ref='g42:time:'+str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result=roots.decide_root_v01(kernel=kernel,decision_input=decision_input)
    require_v01(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=decision_input,result=result),'g42_root_validation')
    return (kernel,decision_input,result),local


def informational_review_v42(live):
    require_v01(live['initial_output']==checks.evaluate_v01(live['initial_material']),'g42_observed_output')
    key=live['initial_artifact'].artifact_id
    return local_review_v42(live,root=ROOT,candidates={key:live['initial_output']},selected=key,scores={key:1000000},
        artifact=live['initial_artifact'],program=live['initial_program'],consent=None,informational=True)[0]


def consume_strategy_v42(live,*,snapshot=None,report=None):
    from hedgehog.gate4_strategy_reference_v01 import validate_reference_strategy_report_v01
    from hedgehog.gate4_reference_contracts_v01 import ReferenceValueV01
    from .gate4_reference_history_v01 import consume_opened_v01
    current_use_v43(live)
    target=live['snapshot'] if snapshot is None else snapshot
    validate_native_domain_v42(native_domain_v42(live['constraints'],target))
    require_v01(canonical_v01(native_domain_v42(live['constraints'],target))==canonical_v01(live['basis']['domain']),'g42_native_source_changed')
    if live['opened'] is not None: consume_opened_v01(live,live['opened'])
    require_v01(canonical_v01(live['host'].current_sources)==canonical_v01(live['basis']['host_sources']),'g42_host_source_changed')
    valid,reasons=work.validate_work_program_result_v01(live['final'].program,live['final'].results,**live['final_common'],host_map={ROOT:live['host']})
    require_v01(valid,'g42_supplied_work:'+repr(reasons))
    output=live['final_output']; actual=json.loads(live['final'].results[-1].result.output[0].value)
    require_v01(output==actual,'g42_actual_final_consumption')
    expected=derive_strategy_v42(live,live['basis'])
    require_v01(expected==live['strategy_inputs'],'g42_original_derivation_changed')
    supplied=output['strategy_report'] if report is None else report
    verified=validate_reference_strategy_report_v01(supplied,inputs=expected,source_basis=expected['context'])
    require_v01(verified.identity==output['strategy_identity'],'g42_strategy_work_identity')
    require_v01(len(output['consumed_quanta'])==len(live['final'].results)-1,'g42_every_quantum_consumed')
    require_v01(output['allocation_identity']==ReferenceValueV01('allocation_report',live['allocation']).identity and output['original_basis_sha256']==digest_v01(live['basis']),'g43_consumed_allocation_binding')
    return verified.plain()


def strategy_reviews_v42(live,*,missing_bank_consent=False,reviewed_at=None):
    report=consume_strategy_v42(live); selected=report['recommendation']
    require_v01(selected is not None,'g42_no_recommendation')
    products={r['id']:int(r['product']) for r in report['scores']}
    values=sorted({products[k] for k in report['pareto']},reverse=True)
    scores={k:1000000-values.index(products[k]) for k in report['pareto']}
    require_v01(sorted(scores,key=lambda k:(-scores[k],k))==report['ranking'],'g42_ordinal_order')
    candidates={key:dict(report=report,original_offer=next(plain_v01(o) for o in live['snapshot'].authoritative_offer_records
        if any(m['kind']=='offer' and m['local_id']==key and m['native_id']==o.offer_id for m in live['basis']['mapping'])),
        exact_product=str(products[key]),ordinal_score=scores[key],score_kind='ORDER_ONLY_NOT_UTILITY_OR_PROBABILITY') for key in report['pareto']}
    offer=candidates[selected]['original_offer']; reviews={}; local={}; consents={}; cross=[]
    for root in ROOTS:
        consent=None if root==binding.AIRLINE_ROOT_ID or (missing_bank_consent and root==binding.BANK_ROOT_ID) else dict(
            root_id=root,offer_id=offer['offer_id'],source_digest=live['snapshot'].candidate_set_digest,max_amount=live['config']['max_amount'],currency=offer['currency'],purpose='PREPARATION_ONLY')
        consents[root]=consent
        reviews[root],local[root]=local_review_v42(live,root=root,candidates=candidates,selected=selected,scores=scores,
            artifact=live['final_artifact'],program=live['final'].program,consent=consent,evaluation_time=None if reviewed_at is None else reviewed_at[root])
        if root!=ROOT:
            ref=multi.build_cross_root_evidence_ref_v01(transaction_id=live['transaction'],source_root_id=ROOT,target_root_id=root,
                evidence_artifact_id=live['final_artifact'].artifact_id,evidence_artifact_hash=digest_v01(live['final_artifact']),
                evidence_class='VALIDATED_EVIDENCE',receipt_validated=False,trace_refs=(reviews[root][1].decision_input_id,live['final'].program.topology_artifact.artifact_id))
            require_v01(not multi.validate_cross_root_evidence_ref_v01(ref),'g42_cross_root_source')
            cross.append(ref)
    envelopes=tuple(multi.build_root_decision_envelope_v01(transaction_id=live['transaction'],root_id=root,
        root_decision_id=r[2].decision_id,source_decision_ref=r[1].decision_input_id,
        outcome_class={'ACCEPT':'ACCEPTED','REJECT':'REJECTED','DEFER':'DEFERRED','BLOCKED_FAIL_CLOSED':'BLOCKED'}.get(r[2].decision,r[2].decision),
        reason_code=r[2].reason_code,selected_subject_id=offer['offer_id'] if r[2].decision=='ACCEPT' else None,
        evidence_refs=(live['final_artifact'].artifact_id,),cross_root_input_refs=tuple(x.ref_id for x in cross if x.target_root_id==root)) for root,r in reviews.items())
    outcome=multi.build_transaction_outcome_envelope_v01(transaction_id=live['transaction'],expected_root_ids=ROOTS,root_decisions=envelopes,cross_root_evidence_refs=tuple(cross))
    require_v01(not multi.validate_transaction_outcome_envelope_v01(outcome),'g42_multiroot')
    return dict(reviews=reviews,local=local,consents=consents,cross=cross,outcome=multi.transaction_outcome_envelope_to_plain_dict_v01(outcome),
        validation=multi.multiroot_validation_result_to_plain_dict_v01(multi.validate_multiroot_v01(outcome)),selected=selected,offer_id=offer['offer_id'],scores=scores)


def prepare_hold_v42(live,reviewed,*,snapshot=None):
    report=consume_strategy_v42(live,snapshot=snapshot)
    require_v01(reviewed['selected']==report['recommendation'],'g42_review_selected_binding')
    expected=strategy_reviews_v42(live,reviewed_at={r:reviewed['local'][r]['now'] for r in ROOTS})
    # Real records must match this current transaction, source, role and terms.
    # Root's time is retained in each input; compare all non-time source material
    # through the local bridge, then validate the exact original Root result.
    for root in ROOTS:
        review=reviewed['reviews'][root]; local=reviewed['local'][root]
        require_v01(not roots.validate_root_decision_result_v01(kernel=review[0],decision_input=review[1],result=review[2])
            and review[2].decision=='ACCEPT' and review[2].target_root_id==root and review[1].transaction_id==live['transaction']
            and review[2].selected_candidate_id==report['recommendation'],'g42_local_acceptance_required')
        require_v01({k:v for k,v in local.items() if k!='now'}=={k:v for k,v in expected['local'][root].items() if k!='now'},'g42_local_current_bridge')
        require_v01(review==expected['reviews'][root],'g42_exact_review_input_binding')
        require_v01(live['clock'].evaluation_time<=local['now']<=current_use_v43(live)['evaluation_time'],'g43_local_review_time')
    historical=reviewed
    reviewed=strategy_reviews_v42(live)
    require_v01(all(r[2].decision=='ACCEPT' for r in reviewed['reviews'].values()),'g43_current_roots_refused')
    validate_native_domain_v42(live['basis']['domain'])
    selection=binding.build_selection_input_v01(binding.build_valid_airline_bsep_projection_ref_v01(),live['constraints'],live['snapshot']); offer_id=reviewed['offer_id']
    require_v01(any(m['kind']=='offer' and m['local_id']==report['recommendation'] and m['native_id']==offer_id for m in live['basis']['mapping']),'g42_native_selected_offer')
    # Explicit evidence-only bridge to the domain's fixed legacy transaction.
    bridge=dict(profile='G42_CHECKED_WORK_ROOT_TO_LEGACY_PREPARATION_V01',work_transaction=live['transaction'],
        legacy_domain_transaction=selection.transaction_id,source_sha256=digest_v01(live['basis']['domain']),
        work_artifact=plain_v01(live['final_artifact']),strategy=report,root_decisions={k:v[2].decision_id for k,v in reviewed['reviews'].items()},offer_id=offer_id)
    ref='g42:domain_bridge:'+digest_v01(bridge)
    evidence=binding.ValidatedAirlineSemanticSelectionEvidenceV01(ref,selection.transaction_id,'g42:local_runtime',live['final_artifact'].artifact_id,
        live['snapshot'].candidate_set_ref,selection.selection_input_id,selection.source_candidate_set_snapshot_id,selection.source_candidate_set_digest,
        ref,offer_id,('exact_native_g4_strategy_work',),(), 'PASS',(),('current_source','actual_work','ordinary_roots'),('permission_transfer',),True,True,False,False,0)
    decision=binding.build_valid_client_root_decision_v01(selection_input=selection,evidence=evidence,selected_offer_id=offer_id,recommendation_accepted=True,root_override_used=False)
    decision=replace(decision,decision_id=reviewed['reviews'][ROOT][2].decision_id)
    resolution=binding.build_valid_airline_root_resolution_v01(selection_input=selection,snapshot=live['snapshot'],decision=decision)
    rr=binding.validate_airline_root_selected_offer_resolution_v01(selection,live['snapshot'],evidence,decision,resolution)
    hold=binding.build_hold_packet_for_offer_v01(live['snapshot'],offer_id)
    link=binding.build_valid_hold_contract_binding_v01(resolution=resolution,hold_packet=hold)
    hr=binding.validate_airline_semantic_hold_contract_binding_v01(resolution,hold,link,resolution_report=rr)
    record=next(r for r in live['snapshot'].authoritative_offer_records if r.offer_id==offer_id)
    offer_packet=replace(binding.corridor_contracts.build_valid_airline_offer_packet_v01(),packet_id=hold.parent_offer_packet_id,
        offer_id=record.offer_id,route_ref=record.route_ref,departure_date=record.departure_date,return_date=record.return_date,
        amount=record.amount,currency=record.currency,baggage_included=record.baggage_included,
        seat_ref='g42:seat_terms:'+digest_v01(record.seat_characteristics),ttl_seconds=record.ttl_seconds,expired=record.expired)
    contract_context=replace(binding.corridor_contracts.build_airline_ticket_purchase_contract_context_from_resolution_v01(
        resolution=resolution,hold_packet=hold),max_amount=live['constraints'].max_amount)
    packet_report=binding.corridor_contracts.validate_airline_hold_commit_packet_v01(offer_packet,hold,contract_context)
    require_v01(rr.validation_status=='PASS' and hr.validation_status=='PASS' and packet_report.validation_status=='PASS','g42_hold_validation:'+repr((rr,hr,packet_report)))
    return dict(status='PREPARATION_ONLY_NOT_EXECUTED',current_use=current_use_v43(live),historical_reviews=historical,current_reviews=reviewed,bridge=bridge,evidence=evidence,decision=decision,resolution=resolution,hold=hold,binding=link,
        resolution_validation=rr,hold_validation=hr,packet_validation=packet_report,offer_packet=offer_packet,contract_context=contract_context)


def start_native_v42(*,label,profile,config,constraints,snapshot,store,journal,task_clock=None):
    from . import gate4_reference_history_v01 as gh
    from hedgehog.gate4_reference_runtime_v01 import literal_v01,local_id_v01 as lid
    from hedgehog.gate4_reference_runtime_v01 import TaskClockV43
    task_clock=TaskClockV43() if task_clock is None else task_clock
    require_v01(type(task_clock) is TaskClockV43,'g43_task_clock')
    claim_ns=time.time_ns(); now=task_clock.now_v01(); task='g42:'+label+':'+str(claim_ns)
    task_clock.bind_v01(task)
    ctx,key,history_policy=gh.keys_v01(config,constraints)
    clock=hosts.TrustedWorkSourceSnapshotV01((),actions.build_logical_time_bridge_v01(origin_utc_epoch_seconds=now,
        seconds_per_tick=1,bridge_policy_version='g42.controlled'),now,'g42.controlled_utc',task,0)
    opened,discovery=store.current_v01(history_key=key,root=ROOT,transaction='transaction:'+task,evaluation_time=now)
    journal.save('history_discovery.json',discovery)
    material=checks.material_v01(constraints,snapshot,snapshot.authoritative_offer_records[0].offer_id,'g42:semantic:'+task)
    catalogue=native_catalogue_v42(); definitions={a.definition.operation_id:a.definition.definition_id for a in catalogue}
    domain=native_domain_v42(constraints,snapshot); manifest=[]
    for b in config['branches']:
        for ordinal,field in enumerate(config['quantum_order'],1):
            q=dict(domain=domain,branch=lid('branch',b['id']),ordinal=ordinal,field=field,offer_id=snapshot.authoritative_offer_records[b['offer_index']].offer_id)
            manifest.append(dict(branch=q['branch'],ordinal=ordinal,work_id=b['id']+'_'+str(ordinal),definition_id=definitions['g42.airline.quantum'],material_sha256=digest_v01(q)))
    need=dict(initial_check=material,finite_catalogue=config,domain=native_domain_v42(constraints,snapshot),
        utility_profile=profile,history=discovery,allowed_quantum_manifest=manifest,definition_roles=definitions)
    source=current_source_v01(task,clock,need)
    env=dict(pt_created_at=utc_v01(now),kt_asof=utc_v01(now),et_observed_at=None,ct_session_anchor=task,
        ttl_seconds=900,freshness_class='static',valid_from=utc_v01(now),valid_to=utc_v01(now+900))
    live=dict(label=label,profile=profile,config=config,constraints=constraints,snapshot=snapshot,store=store,clock=clock,
        claim_ns=claim_ns,task_id=task,transaction='transaction:'+task,env=env,source=source,initial_material=material,
        semantic_ref='g42:semantic:'+task,history_context=ctx,history_key=key,history_policy=history_policy,opened=opened,
        history_evidence_binding=discovery,task_clock=task_clock)
    if opened is not None: gh.consume_opened_v01(live,opened)
    claim=gh.claim_v01(live); live['claim']=claim
    journal.save('prospective.json',claim)
    proposal=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g42:proposal:'+digest_v01(need),artifact_type='SemanticArchitectProposal',
        schema_version='v1',transaction_id=live['transaction'],owner_root_id=ROOT,source_component='semantic_architect',authority_class='ADVISORY',
        lifecycle_state='PROPOSED',payload=need,trace_refs=('g42:intent:'+task,),parent_refs=(source.bsep_packet['packet_id'],claim.artifact_id),time_envelope=env)
    common=dict(catalogue=catalogue,source_context=source,semantic_proposal=proposal)
    item=work.WorkItemV01('constraint',definitions['atlas.airline.constraint'],ROOT,(literal_v01('material',material),),(),(),None,None)
    bc=config['original_budget']
    candidate=work.build_work_program_candidate_v01(task_id=task,previous_revision_id=None,intent_ref='g42:intent:'+task,
        bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,
        budget=work.WorkBudgetV01(*(bc[k] for k in ('max_items','max_children','max_model_calls','max_compute_units','max_revisions'))),
        items=(item,),trigger_evidence_refs=(),**common)
    policy=work.build_work_task_policy_v01(candidate,**common,host_instance_ref='host:'+ROOT,definition_ids=tuple(sorted(definitions.values())),resource_refs=())
    class Source:
        reads=0
        def read_current_v01(self):
            self.reads+=1
            return clock
    trusted=Source()
    host=hosts.build_root_work_execution_host_v01(owning_root_id=ROOT,registry=actions.build_empty_action_commit_packet_registry_v02(),catalogue=catalogue,
        packet_bindings=(),current_dependency_observations=(),logical_time_bridge=clock.logical_time_bridge,trusted_source=trusted,task_policies=(policy,))
    program=work.materialize_work_program_v01(candidate,**common)
    context=work.enroll_work_program_v01(host,program,**common,expected_revision=host.state_revision)
    journal.save('enrolled.json',dict(policy=policy,proposal=proposal,source=source,program=program,snapshot=work.inspect_work_task_v01(host,task_id=task),
        catalogue=tuple(firewall.snapshot_admitted_capability_v01(a) for a in catalogue)))
    outcome=work.advance_work_program_v01(program,**common,host_map={ROOT:host},continuation_context=context)
    require_v01(outcome.status=='COMPLETED','g42_initial_check:'+repr(outcome))
    event_ns=time.time_ns(); artifact=work.work_program_result_to_artifact_v01(program,outcome.results,**common,host_map={ROOT:host})
    live.update(catalogue=catalogue,definitions=definitions,proposal=proposal,common=common,policy=policy,host=host,trusted=trusted,
        initial_program=program,initial_results=outcome.results,initial_output=json.loads(outcome.results[0].result.output[0].value),
        initial_artifact=artifact,event_ns=event_ns)
    journal.save('initial_completed.json',dict(result=outcome,artifact=artifact,observed_wall_ns=str(event_ns)))
    return live


def native_story_v42(directory,*,controlled_clock=False):
    """Three finite comparison instances; no task reset inside a continuation."""
    from . import gate4_reference_history_v01 as gh
    from hedgehog.gate4_reference_runtime_v01 import local_id_v01 as lid
    from hedgehog.gate4_reference_runtime_v01 import TaskClockV43
    journal=JournalV01(directory); config=native_config_v42(); config={**config,**config['source']}
    journal.save('frozen_configuration.json',config)
    with journal.phase('shared_native_source'):
        constraints,snapshot,selection,_,reports=controlled_source_v01(config,int(time.time()),'g42:shared:'+str(time.time_ns()))
        journal.save('original_domain.json',dict(domain=native_domain_v42(constraints,snapshot),validation=reports))
        store=history.OutcomeHistoryV01(journal.directory/'history',trusted_events=())
    lives={}; evidence={}
    for label,profile in (('cold','PRICE_FIRST'),('contrast','COMFORT_FIRST'),('warm','PRICE_FIRST')):
        sub=JournalV01(journal.directory/label)
        with journal.phase(label+'_setup_and_initial'):
            live=start_native_v42(label=label,profile=profile,config=config,constraints=constraints,snapshot=snapshot,store=store,journal=sub,
                task_clock=TaskClockV43(int(time.time())) if controlled_clock else None)
        with journal.phase(label+'_allocation_and_native_work'): run_allocated_v42(live,sub)
        with journal.phase(label+'_root_and_domain_consumption'):
            reviewed=strategy_reviews_v42(live); hold=prepare_hold_v42(live,reviewed)
            sub.save('reviews.json',reviewed);sub.save('domain_consumption.json',hold)
            sub.save('current_use.json',live['current_use_events'])
            sub.save('current_history.json',live.get('current_history_evidence',[]))
            sub.save('portable_records.json',dict(
                admissions=feedback.g35_record_to_plain_v01(tuple(firewall.snapshot_admitted_capability_v01(x) for x in live['catalogue'])),
                initial_program=feedback.g35_record_to_plain_v01(live['initial_program']),
                initial_results=feedback.g35_record_to_plain_v01(live['initial_results']),
                final_program=feedback.g35_record_to_plain_v01(live['final'].program),
                final_results=feedback.g35_record_to_plain_v01(live['final'].results),
                roots={r:[feedback.g35_record_to_plain_v01(x) for x in v] for r,v in reviewed['reviews'].items()},
                current_roots={r:[feedback.g35_record_to_plain_v01(x) for x in v] for r,v in hold['current_reviews']['reviews'].items()}))
            sub.save('domain_records.json',feedback.g35_record_to_plain_v01({k:hold[k] for k in
                ('evidence','decision','resolution','hold','binding','offer_packet','contract_context')}))
        lives[label]=live; evidence[label]=dict(reviews=reviewed,hold=hold)
        if label=='contrast':
            # Both cold comparisons precede the one observation's recording.
            with journal.phase('g3_observation_recording'):
                event,proof=gh.observe_v01(lives['cold'],journal)
                store=history.OutcomeHistoryV01(journal.directory/'history',trusted_events=(event,))
                prepared,review=store.prepare_v01((json.loads(event.feedback_canonical)['feedback_id'],),expected_head=None,evaluated_at=int(time.time()))
                head=store.commit_v01(prepared,review,expected_head=None)
                journal.save('history_recorded.json',dict(snapshot=prepared.to_plain_data(),review=review,head=head,
                    root_records=[feedback.g35_record_to_plain_v01(x) for x in review]))
    with journal.phase('causal_comparisons'):
        fixed=lambda live:dict(domain=live['basis']['domain'],configuration=live['config'],policy_values={k:getattr(live['policy'],k) for k in ('max_items','max_children','max_model_calls','max_compute_units','max_revisions')})
        cold,warm,contrast=lives['cold'],lives['warm'],lives['contrast']
        require_v01(fixed(cold)==fixed(warm)==fixed(contrast),'g42_fixed_comparison_inputs')
        require_v01(cold['opened'] is None and contrast['opened'] is None and warm['opened'] is not None,'g42_history_order')
        counts=lambda live:{b['id']:next(r['allocation'] for r in live['allocation']['rows'] if r['id']==lid('branch',b['id'])) for b in config['branches']}
        performed=lambda live:[r.work_id for r in live['final'].results if r.work_id!='final_strategy']
        require_v01(counts(cold)!=counts(warm) and performed(cold)!=performed(warm),'g42_cp_budget_no_causal_change')
        require_v01(evidence['cold']['hold']['hold'].offer_id!=evidence['contrast']['hold']['hold'].offer_id,'g42_cp_strategy_no_causal_change')
        comparison=dict(fixed=fixed(cold),declared_differences=config['comparison']['legitimate_differences'],
            cp_strategy=dict(profiles=[cold['profile'],contrast['profile']],selected=[evidence['cold']['hold']['hold'].offer_id,evidence['contrast']['hold']['hold'].offer_id],
                actual_root_decisions={label:{r:v[2].decision_id for r,v in evidence[label]['reviews']['reviews'].items()} for label in ('cold','contrast')}),
            cp_budget=dict(cold_prior=0,actual_raw_prior=gh.consume_opened_v01(warm,warm['opened']),cold=counts(cold),warm=counts(warm),
                cold_performed=performed(cold),warm_performed=performed(warm),mandatory=config['mandatory'],prior_applications=1))
        journal.save('comparisons.json',comparison)
    summary=dict(result='G42_NATIVE_STORY_COMPARISONS_COMPLETE',phase_seconds=journal.times,
        comparisons=comparison,instances={label:dict(compute_units=live['final'].snapshot.usage.compute_units,
            cap=live['policy'].max_compute_units,dispatches=len(live['host'].work_attempts),revisions=live['final'].snapshot.usage.revisions,
            trusted_source_reads=live['trusted'].reads,model_calls=live['final'].snapshot.usage.model_calls) for label,live in lives.items()},
        source_admission='UNADMITTED_PENDING_INDEPENDENT_REVIEW',full_gate4='NOT_CLAIMED',real_business_effects=0)
    journal.save('summary.json',summary)
    return dict(lives=lives,evidence=evidence,summary=summary,journal=journal,store=store,proof=proof,event=event)


def run_allocated_v42(live,journal):
    from copy import deepcopy
    from hedgehog.gate4_reference_runtime_v01 import NativeAllocationConsumerV01,NativeWorkInventoryV01,literal_v01,local_id_v01 as lid
    from hedgehog.gate4_pressure_budget_v01 import allocate_reference_work_budget_v01,evaluate_reference_pressure_v01
    from hedgehog.gate4_reference_contracts_v01 import G4_REFERENCE_NUMERIC_V01
    basis=native_basis_v42(live); strategy=derive_strategy_v42(live,basis)
    domain=basis['domain']; quanta=[]; branches=[]
    for b in live['config']['branches']:
        offer=live['snapshot'].authoritative_offer_records[b['offer_index']]; branch=lid('branch',b['id']); items=[]
        for ordinal,field in enumerate(live['config']['quantum_order'],1):
            descriptor=dict(branch=branch,ordinal=ordinal,field=field,offer_id=offer.offer_id); quanta.append(descriptor)
            material=dict(domain=domain,**descriptor)
            items.append(work.WorkItemV01(b['id']+'_'+str(ordinal),live['definitions']['g42.airline.quantum'],ROOT,(literal_v01('material',material),),(),(),None,None))
        branches.append((branch,tuple(items)))
    final_material=dict(domain=domain,initial_material=live['initial_material'],quanta=quanta,strategy_inputs=strategy,independent_context=strategy['context'])
    budget=derive_budget_v42(live,basis,final_material)
    pressure=evaluate_reference_pressure_v01(budget['pressure_inputs'],profile=G4_REFERENCE_NUMERIC_V01)
    allocation=allocate_reference_work_budget_v01(pressure,current_budget_context=budget).plain()
    context=work.work_continuation_context_v01(live['host'],task_id=live['task_id'],expected_revision=live['host'].state_revision)
    trigger=work.build_work_revision_trigger_v01(context,work_id='constraint',output_field='material')
    inventory=NativeWorkInventoryV01(tuple(branches),live['definitions']['g42.airline.strategy'],canonical_v01(final_material))
    consumer=NativeAllocationConsumerV01(host=live['host'],task_id=live['task_id'],common=live['common'],inventory=inventory,budget=budget,trigger=trigger,original_basis=basis,
        history_store=live['store'],task_clock=live['task_clock'])
    items=consumer.expected_items_v01(allocation); kwargs=dict(proposed_items=items,current_budget_context=budget,original_basis=basis)
    controls={}; original_attempts=len(live['host'].work_attempts)
    from hedgehog.gate4_reference_contracts_v01 import digest
    before_state=work.inspect_work_task_v01(live['host'],task_id=live['task_id'])
    constructor_controls={}
    for name in ('coherent_6_1','coherent_cold_prior','coherent_source_identity','coherent_feature'):
        changed=deepcopy(budget); p=changed['pressure_inputs']
        if name=='coherent_6_1':
            for row in p['branches']:row['lower']=row['upper']=6 if row['id']==lid('branch','offer_0') else 1
        elif name=='coherent_cold_prior':p['branches'][0]['prior'].update(value=500000000,disposition='USABLE')
        elif name=='coherent_source_identity':p['context']['transaction_id']='g4_reference:foreign_transaction'
        else:p['branches'][0]['cost']['value']+=1
        p['context']['source_snapshot_hash']=digest(p['branches']);p['context']['candidate_set_hash']=digest([r['id'] for r in p['branches']])
        changed['context']=deepcopy(p['context'])
        if name=='coherent_source_identity':
            changed['spending_snapshot_hash']=digest(dict(spent=changed['spent'],host_revision=changed['host_revision'],
                owner_root_id=changed['context']['owner_root_id'],task_id=changed['context']['task_id'],transaction_id=changed['context']['transaction_id']))
        coherent=allocate_reference_work_budget_v01(evaluate_reference_pressure_v01(p,profile=G4_REFERENCE_NUMERIC_V01),current_budget_context=changed).plain()
        try:
            bad=NativeAllocationConsumerV01(host=live['host'],task_id=live['task_id'],common=live['common'],inventory=inventory,
                budget=changed,trigger=trigger,original_basis=basis,history_store=live['store'],task_clock=live['task_clock'])
            bad.validate_v01(coherent,proposed_items=bad.expected_items_v01(coherent),current_budget_context=changed,original_basis=basis)
        except ValueError as error:constructor_controls[name]=dict(reason=str(error),budget=changed,allocation=coherent)
        else:raise AssertionError('g43_new_consumer_accepted:'+name)
        require_v01(before_state==work.inspect_work_task_v01(live['host'],task_id=live['task_id']) and len(live['host'].work_attempts)==original_attempts,'g43_refusal_changed_usage')
        consumer.validate_v01(allocation,**kwargs)
    journal.save('constructor_controls.json',dict(controls=constructor_controls,before=before_state,
        after=work.inspect_work_task_v01(live['host'],task_id=live['task_id']),attempts=original_attempts))
    controls['constructor_refusals']=constructor_controls
    variants=dict(extra_quantum=items+(branches[0][1][-1],),unlisted_definition=(replace(items[0],definition_id='g42:unlisted'),)+items[1:],
        unlisted_material=(replace(items[0],inputs=(literal_v01('material',dict(domain=domain,**quanta[-1])),)),)+items[1:],
        out_of_quota_ordinal=(branches[0][1][-1],)+items[1:],duplicate_terminal=(replace(items[0],work_id='constraint'),)+items[1:])
    for name,bad in variants.items():
        try: consumer.validate_v01(allocation,**dict(kwargs,proposed_items=bad))
        except ValueError as error: controls[name]=str(error)
        else: raise AssertionError('g42_negative_accepted:'+name)
        consumer.validate_v01(allocation,**kwargs)
    altered=deepcopy(basis); altered['time_envelope']['kt_asof']=utc_v01(live['clock'].evaluation_time+1)
    for name,changed in [('wrong_original_time',dict(original_basis=altered)),('wrong_budget_revision',dict(current_budget_context=dict(budget,host_revision=budget['host_revision']+1)))]:
        try: consumer.validate_v01(allocation,**dict(kwargs,**changed))
        except ValueError as error: controls[name]=str(error)
        else: raise AssertionError('g42_negative_accepted:'+name)
        consumer.validate_v01(allocation,**kwargs)
    require_v01(len(live['host'].work_attempts)==original_attempts,'g42_negative_dispatched')
    journal.save('allocation_before_install.json',dict(basis=basis,strategy_inputs=strategy,final_material=final_material,budget=budget,
        allocation=allocation,trigger=trigger,approved_items=items,controls=controls,native_attempts_before=original_attempts))
    revision=consumer.install_v01(allocation,**kwargs)
    require_v01(revision.program is not None,'g42_revision:'+repr(revision))
    context2=work.work_continuation_context_v01(live['host'],task_id=live['task_id'],expected_revision=live['host'].state_revision)
    common=dict(live['common'],continuation_context=context2)
    final=work.advance_work_program_v01(revision.program,**common,host_map={ROOT:live['host']})
    require_v01(final.status=='COMPLETED','g42_final_work:'+repr(final))
    artifact=work.work_program_result_to_artifact_v01(final.program,final.results,**common,host_map={ROOT:live['host']})
    output=json.loads(final.results[-1].result.output[0].value)
    live.update(basis=basis,strategy_inputs=strategy,budget=budget,allocation=allocation,final=final,final_artifact=artifact,
        final_common=common,final_output=output,consumer=consumer,consumer_kwargs=kwargs,controls=controls)
    require_v01(final.snapshot.policy==live['policy'] and final.snapshot.usage.compute_units==live['policy'].max_compute_units,'g42_enrolled_cumulative_cap')
    try: consumer.validate_v01(allocation,**kwargs)
    except ValueError as error: controls['stale_spending_revision']=str(error)
    else: raise AssertionError('g42_stale_allocation_accepted')
    fresh=work.work_continuation_context_v01(live['host'],task_id=live['task_id'],expected_revision=live['host'].state_revision)
    retry=work.advance_work_program_v01(final.program,**dict(live['common'],continuation_context=fresh),results=final.results,host_map={ROOT:live['host']})
    require_v01(retry.snapshot==final.snapshot and retry.results==final.results,'g42_terminal_retry')
    controls['terminal_retry']='UNCHANGED_NO_CHARGE'
    final_trigger=work.build_work_revision_trigger_v01(fresh,work_id='final_strategy',output_field='material')
    exhausted=work.revise_work_program_v01(fresh,previous_revision_id=final.program.candidate.revision_id,trigger=final_trigger,items=items,
        budget=work.WorkBudgetV01(16,0,0,1,0),**live['common'])
    require_v01(exhausted.status=='EXHAUSTED','g42_native_exhaustion:'+repr(exhausted))
    controls['exhaustion']=plain_v01(exhausted)
    journal.save('completed_work.json',dict(final=final,artifact=artifact,output=output,attempts=live['host'].work_attempts,
        after=work.inspect_work_task_v01(live['host'],task_id=live['task_id']),controls=controls,trusted_source_reads=live['trusted'].reads))
    return live
