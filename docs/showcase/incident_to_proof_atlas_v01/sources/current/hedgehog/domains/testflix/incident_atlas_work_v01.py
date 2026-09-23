"""Finite Testflix constraint Work and the generic G34 predictive history route.

No payment, replacement scorer or authority from a recorded prediction.
"""
import hashlib
import json
import time
from pathlib import Path

from hedgehog import action_commit_packet_v02 as actions, work_execution_host_v01 as hosts
from hedgehog import outcome_feedback_v01 as feedback, outcome_calibration_v01 as cal
from hedgehog import outcome_feedback_history_v01 as history, outcome_feedback_consumer_v01 as consumer
from hedgehog import avf_v02 as avf
from hedgehog.kernel import abi_v01 as abi, effect_firewall_v01 as fw, work_composition_v01 as work
from hedgehog.incident_atlas_v01 import canonical_v01 as canonical, digest_v01 as digest, require_v01 as require
from hedgehog.incident_atlas_history_v01 import storage_projection_v01
from . import contracts_v01 as contracts
from .incident_atlas_source_v01 import current_source_v01, output_review_v01

ROOT = 'root:testflix:user'
OPERATION = 'TESTFLIX_CURRENT_START_CHECK'


def values(records):
    return {v.parameter_name: v.value for v in records}


def material_v01(prepared, event, entitlement, devices, semantic_ref):
    from dataclasses import asdict
    clock=prepared['source'].read_current_v01()
    observed=feedback.g35_record_to_plain_v01(clock.observations)
    return dict(checks=[dict(semantic_ref=semantic_ref,session_id=event.entitlement_id + ':' + prepared['bound'].packet_identity.packet_id,
        observations=[dict(observation_id='testflix:current:' + digest(observed), observed=observed)])],
        policy=dict(predicate='Current native session and paid/device scope support this exact START.',
            owning_root='root:testflix:device',operation='testflix.playback.v01'),
        event=asdict(event), entitlement=asdict(entitlement), devices=[asdict(d) for d in devices], active=[],
        clock=dict(evaluation_time=clock.evaluation_time,source=clock.evaluation_time_source,context=clock.evaluation_context_id),
        canonical=feedback.g35_record_to_plain_v01(prepared['bound'].canonical_projection))


def entitlement_v01(value):
    c=value['candidate'];c=dict(c,plan=contracts.PlanV01(**c['plan']))
    return contracts.EntitlementV01(contracts.EntitlementCandidateV01(**c),value['decision_id'],value['issuance_receipt_ref'])


def evaluate_v01(material, *, provenance=False):
    require(set(material)=={'checks','policy','event','entitlement','devices','active','clock','canonical'} and len(material['checks'])==1,'atlas_testflix_material')
    check=material['checks'][0];event=contracts.PlaybackRequestV01(**material['event'])
    entitlement=entitlement_v01(material['entitlement'])
    devices=tuple(contracts.DeviceStateV01(**dict(d,permitted_content_ids=tuple(d['permitted_content_ids']))) for d in material['devices'])
    packet=feedback.g35_record_from_plain_v01(material['canonical'])
    observations=feedback.g35_record_from_plain_v01(check['observations'][0]['observed'])
    require(check['observations'][0]['observation_id']=='testflix:current:'+digest(check['observations'][0]['observed']),'atlas_testflix_observation')
    reasons=[]
    try:contracts.validate_playback_request_v01(event,entitlement,devices,tuple(material['active']),material['clock']['evaluation_time']-4)
    except ValueError as error:reasons.append(str(error))
    now=material['clock']['evaluation_time']
    if not packet.temporal_authority.issued_at_utc<=now<packet.temporal_authority.expires_at_utc:reasons.append('action_current_time')
    if packet.owning_local_root_id!=material['policy']['owning_root']:reasons.append('owning_root')
    for dependency in packet.dependency_candidate.dependency_records:
        rows=[v for v in observations if v.dependency_id==dependency.dependency_id]
        if len(rows)!=1 or rows[0].observed_content_sha256!=dependency.content_sha256 or not rows[0].valid_from_utc<=now<rows[0].valid_to_utc:
            reasons.append('current_dependency')
    if provenance:
        require(actions.validate_native_action_commit_packet_v01(packet)[0] and all(actions.validate_action_dependency_current_observation_v01(v)[0] for v in observations),'atlas_testflix_native_provenance')
    return dict(stage='RESULT',checks=[dict(healthy=not reasons,semantic_ref=check['semantic_ref'])],semantic_refs=[check['semantic_ref']],
        input_sha256=digest(material),session_id=check['session_id'],provenance_checked=provenance,source_validation=reasons)


def input_validator_v01(definition, inputs):
    errors = fw.validate_capability_values_v01(definition.input_fields, inputs)
    if not errors:
        try:
            evaluate_v01(json.loads(values(inputs)['material']))
        except (ValueError, TypeError, KeyError):
            errors = ('atlas_testflix_input',)
    return fw.build_capability_validation_evidence_v01(definition=definition, values=inputs, invocation_id=None, valid=not errors, reason_codes=errors)


def execute_constraint_v01(invocation):
    output = evaluate_v01(json.loads(values(invocation.inputs)['material']))
    return (actions.ActionEffectParameterRecordV01('material', 'TEXT', canonical(output).decode()),)


def execute_provenance_v01(invocation):
    output = evaluate_v01(json.loads(values(invocation.inputs)['material']), provenance=True)
    return (actions.ActionEffectParameterRecordV01('material', 'TEXT', canonical(output).decode()),)


def output_validator_v01(definition, invocation, output):
    errors = fw.validate_capability_values_v01(definition.output_fields, output)
    if not errors:
        expected = evaluate_v01(json.loads(values(invocation.inputs)['material']), provenance=definition.operation_id == 'atlas.testflix.provenance')
        if json.loads(values(output)['material']) != expected:
            errors += ('atlas_testflix_output',)
    return fw.build_capability_validation_evidence_v01(definition=definition, values=output, invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def catalogue_v01():
    result = []
    for name, executor in (('constraint', execute_constraint_v01), ('provenance', execute_provenance_v01)):
        functions = (input_validator_v01, output_validator_v01, executor)
        codes = tuple(hosts.observe_local_capability_code_v01(f) for f in functions)
        definition = fw.build_capability_definition_v01(operation_id='atlas.testflix.' + name, version='v01', effect_kind='PURE', business_semantics=None,
            input_fields=(fw.build_capability_field_v01(name='material', value_type='TEXT', required=True, consequential=False),),
            output_fields=(fw.build_capability_field_v01(name='material', value_type='TEXT', required=True, consequential=False),), resource_refs=(),
            input_validator_ref=codes[0].public_symbol, output_validator_ref=codes[1].public_symbol, executor_ref=codes[2].public_symbol,
            code_sha256s=tuple((v.public_symbol, v.source_sha256) for v in codes))
        result.append(hosts.admit_local_capability_v01(definition=definition, input_validator=functions[0], output_validator=functions[1],
            executor=executor, catalogue_revision=0, host_instance_ref='host:' + ROOT))
    return tuple(result)


def subject_v01(material, strategy='constraint'):
    revision = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    policy = 'policy:' + digest(material['policy'])
    subject = dict(local_root_scope_id=ROOT, domain_scope_id='TESTFLIX', pack_family_id='REVOCABLE_ACTION',
        advisory_source_class='CONTROLLED_TESTFLIX_CONSTRAINT_PROPOSAL' if strategy == 'constraint' else 'CONTROLLED_TESTFLIX_PROVENANCE_REVIEW',
        advisory_source_revision=revision, advice_claim_profile_id=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
        route_family_id='PURE_TESTFLIX_' + strategy.upper(), task_risk_class='INFORMATIONAL',
        validation_profile_id='G34_TYPED_BOOLEAN_COMPLETED_WORK_V01', policy_semantics_version=policy, history_key_profile_id='G3_TYPED_HISTORY_KEY_V01')
    key = {k: subject[k] for k in feedback._HISTORY_FIELDS if k in subject}
    key.update(task_class_id=OPERATION, capability_contract_version='atlas.testflix.check.v01', evidence_validation_profile_id=subject['validation_profile_id'])
    return subject, key


def execute_current_v01(material, *, invocation, catalogue, store=None, history_key=None, only_constraint=False, check_request=None, evaluation_time=None, shared_host=None):
    now = int(time.time()) if evaluation_time is None else evaluation_time
    if check_request is not None:
        invocation = 'g34:check:' + check_request['check_id']
    clock = hosts.TrustedWorkSourceSnapshotV01((), actions.build_logical_time_bridge_v01(origin_utc_epoch_seconds=now,
        seconds_per_tick=1, bridge_policy_version='atlas.testflix.current'), now, 'atlas.controlled_utc', 'atlas:testflix', 0)
    class Source:
        def __init__(self): self.reads = 0
        def read_current_v01(self): self.reads += 1; return clock
    trusted_source = Source()
    host = shared_host
    if host is None:
        host = hosts.build_root_work_execution_host_v01(owning_root_id=ROOT, registry=actions.build_empty_action_commit_packet_registry_v02(),
            catalogue=catalogue, packet_bindings=(), current_dependency_observations=(), logical_time_bridge=clock.logical_time_bridge, trusted_source=trusted_source)
    source = current_source_v01(invocation, clock, material)
    transaction = 'transaction:' + invocation
    opened, discovery = store.current_v01(history_key=history_key, root=ROOT, transaction=transaction, evaluation_time=now) if store else (None, {'reason':'EXPLICIT_COLD_START'})
    env = dict(pt_created_at=feedback._utc(now), kt_asof=feedback._utc(now), et_observed_at=None, ct_session_anchor=invocation,
        ttl_seconds=3600, freshness_class='static', valid_from=feedback._utc(now), valid_to=feedback._utc(now+3600))
    bridge = opened['bridge'] if opened else abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='atlas:cold:' + digest(dict(transaction=transaction, now=now)),
        artifact_type='SemanticEvidence', schema_version='v1', transaction_id=transaction, owner_root_id=ROOT, source_component='atlas_testflix_history',
        authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED', payload=dict(profile='G34_COLD_HISTORY_V01', prior_fp=0), trace_refs=(invocation,), parent_refs=(), time_envelope=env)
    strategies = ('provenance',) if check_request is not None else ('constraint',) if only_constraint else ('constraint', 'provenance')
    claims = {}; keys = {}
    for strategy in strategies:
        subject, key = subject_v01(material, strategy)
        admission = next(a for a in catalogue if a.definition.operation_id == 'atlas.testflix.' + strategy)
        claim = dict(operation=admission.definition.operation_id, definition_id=admission.definition.definition_id, material_sha256=digest(material),
            observation_refs=[r['observation_id'] for r in material['checks'][0]['observations']], subject=subject, history_key=key)
        claim['claim_id'] = consumer.identity('current_claim', claim); claims[strategy] = claim; keys[strategy] = key
    checks = {}
    for strategy, claim in claims.items():
        check = dict(profile='G34_BOUNDED_CURRENT_ADEQUACY_V01', root=ROOT, target_claim_id=claim['claim_id'], target_subject=claim['subject'],
            observation_refs=claim['observation_refs'], task_inputs_sha256=digest(material), epoch=opened['head'] if opened else None,
            evaluated_at=now, policy_ref=subject_v01(material)[0]['policy_semantics_version'], operation='atlas.testflix.provenance',
            definition_id=next(a.definition.definition_id for a in catalogue if a.definition.operation_id=='atlas.testflix.provenance'),
            material=material, result_facts=evaluate_v01(material, provenance=True))
        check['check_id'] = consumer.identity('bounded_check', check)
        checks[strategy] = None if check_request is not None else check
    contract = consumer.build_current_review_contract_v01(source_context=source, root=ROOT, transaction=transaction,
        policy_ref=subject_v01(material)[0]['policy_semantics_version'], claims=claims, checks=checks,
        role='EVIDENCE_CHECK' if check_request is not None else 'MAIN', check_request=check_request)
    # Fixed declared costs, not chosen from the observed result or a desired winner.
    candidates = tuple(avf.AVFCandidateV02(candidate_id=s, candidate_label=claims[s]['operation'], base_viability_score=0.79 if s=='constraint' else 0.80, ttl_valid=True) for s in strategies)
    trusted = dict(candidates=candidates, history_keys=keys, opened_history=opened, bridge=bridge, evaluated_at=now, contract=contract, source_context=source)
    projection, reports = consumer.build_current_advisory_v01(**trusted)
    review = consumer.review_current_advisory_v01(projection=projection, trusted_inputs=trusted, root=ROOT, transaction=transaction, candidate_materials=claims)
    initial_review = feedback.g35_record_to_plain_v01(review)
    additional = None; additional_receipt = None; receipt_bridge = None
    if review[2].decision == 'NEEDS_MORE_EVIDENCE':
        require(check_request is None, 'atlas_testflix_nonrecursive_check')
        check = checks[projection.to_plain_data()['selected']]
        additional, check_live = execute_current_v01(material, invocation='', catalogue=catalogue, check_request=check, evaluation_time=now, shared_host=host)
        additional_receipt = (check_live['program'], check_live['results'], check_live['common'], {ROOT:check_live['host']})
        review = consumer.review_current_advisory_v01(projection=projection, trusted_inputs=trusted, root=ROOT, transaction=transaction,
            candidate_materials=claims, additional_receipt=additional_receipt)
        receipt_bridge = consumer.current_check_receipt_bridge_v01(check=check, receipt=additional_receipt, current_bridge=bridge)
    require(review[2].decision == 'ACCEPT', 'atlas_testflix_current_review:' + review[2].decision)
    projected = projection.to_plain_data(); selected = projected['selected']; claim = claims[selected]
    payload = dict(material=material, advisory_ref=projected['projection_id'], bridge_ref=bridge.artifact_id,
        root_decision_ref=review[2].decision_id, operation=claim['operation'], check_request=check_request, check_receipt_ref=receipt_bridge.artifact_id if receipt_bridge else None)
    proposal = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='atlas:proposal:' + digest(payload), artifact_type='SemanticArchitectProposal',
        schema_version='v1', transaction_id=transaction, owner_root_id=ROOT, source_component='semantic_architect', authority_class='ADVISORY', lifecycle_state='PROPOSED',
        payload=payload, trace_refs=('g34:intent:' + invocation, review[2].decision_id),
        parent_refs=(source.bsep_packet['packet_id'], bridge.artifact_id, 'g34:advisory:' + projected['projection_id']) + ((receipt_bridge.artifact_id,) if receipt_bridge else ()), time_envelope=env)
    item = work.WorkItemV01('check', claim['definition_id'], ROOT, (work.WorkInputBindingV01('material', work.WorkLiteralV01(
        actions.ActionEffectParameterRecordV01('material', 'TEXT', canonical(material).decode()))),), (), (), None, None)
    program, results, artifact, common = consumer.execute_reviewed_pure_work_v01(review=review, projection=projection, source_context=source,
        semantic_proposal=proposal, catalogue=catalogue, host=host, item=item, material=material, budget=work.WorkBudgetV01(1,0,0,1,0), task_id=invocation, trusted_inputs=trusted, additional_receipt=additional_receipt)
    output = json.loads(values(results[0].result.output)['material'])
    final_review = output_review_v01(root=ROOT, transaction=transaction, candidates={artifact.artifact_id:output}, selected=artifact.artifact_id,
        scores={artifact.artifact_id:1000000}, evidence_ref=artifact.artifact_id, now=now, predicate='atlas_testflix_completed_check', topology_ref=program.topology_artifact.artifact_id)
    source_plain = {k:getattr(source,k) for k in ('business_request_context_packet','bsep_packet','bsep_route_context_packet','bsep_orchestrator_proposal','bsep_structured_rationale')}
    saved = dict(material=material, source=source_plain, projection=projected, reports=reports,
        contract=contract.to_plain_data(), bridge=abi.kernel_artifact_to_plain_dict_v01(bridge), discovery=discovery,
        current_review=feedback.g35_record_to_plain_v01(review), output_review=feedback.g35_record_to_plain_v01(final_review),
        proposal=abi.kernel_artifact_to_plain_dict_v01(proposal), program=feedback.g35_record_to_plain_v01(program), results=feedback.g35_record_to_plain_v01(results),
        admissions=feedback.g35_record_to_plain_v01(tuple(fw.snapshot_admitted_capability_v01(a) for a in catalogue)),
        artifact=abi.kernel_artifact_to_plain_dict_v01(artifact), output=output, source_reads=trusted_source.reads if shared_host is None else None,
        initial_review=initial_review, additional=additional, receipt_bridge=abi.kernel_artifact_to_plain_dict_v01(receipt_bridge) if receipt_bridge else None)
    return saved, dict(host=host, program=program, results=results, common=common, review=final_review, artifact=artifact, material=canonical(material))


def observe_v01(directory, material, catalogue):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    invocation = 'atlas:testflix:prediction'
    claim_ns = time.time_ns(); now = claim_ns // 10**9
    semantic = material['checks'][0]['semantic_ref']; subject, key = subject_v01(material)
    payload = dict(profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID, predicted=True, expected_fp=1000000, claim_wall_ns=str(claim_ns),
        dependencies_sha256=digest(material), semantic_ref=semantic, operation=OPERATION,
        source_observation_refs=[r['observation_id'] for r in material['checks'][0]['observations']], policy_ref=subject['policy_semantics_version'],
        valid_from=now, valid_to=now+604800, sequence=1)
    envelope = dict(pt_created_at=feedback._utc(now), kt_asof=feedback._utc(now), et_observed_at=None, ct_session_anchor=invocation,
        ttl_seconds=604800, freshness_class='static', valid_from=feedback._utc(now), valid_to=feedback._utc(now+604800))
    claim = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='g34:prediction:' + digest(payload), artifact_type='SemanticEvidence', schema_version='v1',
        transaction_id='transaction:' + invocation, owner_root_id=ROOT, source_component='atlas_testflix_prediction', authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED',
        payload=payload, trace_refs=(semantic,), parent_refs=(), time_envelope=envelope)
    (directory/'prospective.json').write_bytes(canonical(abi.kernel_artifact_to_plain_dict_v01(claim)))
    started = time.monotonic_ns()
    saved, live = execute_current_v01(material, invocation=invocation, catalogue=catalogue, only_constraint=True)
    event_ns = time.time_ns(); capture_ns = time.time_ns()
    closure = {str(Path(__file__).name): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    occurrence = 'atlas:occurrence:' + digest(payload); capture = 'atlas:capture:' + digest(saved)
    context = dict(subject)
    context.pop('domain_scope_id'); context.update(domain='TESTFLIX', source_id='atlas:context:' + digest(material),
        task_class_id=OPERATION, capability_contract_version=key['capability_contract_version'], transaction_id='transaction:' + invocation,
        run_id=invocation, episode_id=invocation, scenario_id='T4_NATIVE_CURRENT_START_PREDICTION')
    operation = dict(operation=OPERATION, object_id=material['checks'][0]['session_id'], recipient=ROOT)
    native = dict(source_profile_id=feedback.NATIVE_SOURCE_PROFILE_ID, evidence_class='NATIVE_CONTROLLED_OBSERVATION', context=context,
        policy=dict(source_id=payload['policy_ref'], revision=payload['policy_ref'], **operation), origin=dict(source_id='atlas:origin:' + semantic, occurrence_id=occurrence),
        proposal=dict(source_id=semantic, origin_ref='atlas:origin:' + semantic, created_at=now, recommendation='PROCEED', **operation),
        expectation=dict(source_id=claim.artifact_id, created_at=now, expected_fp=payload['expected_fp']),
        observation=dict(source_id=capture, proposal_ref=semantic, occurrence_ref=occurrence, **operation, result_revision=key['capability_contract_version'],
            event_time=event_ns//10**9, boundary_disposition='PERMITTED', effect_count=0, result_state='PRESENT', failure='NONE'),
        closure=dict(source_id='atlas:closure:' + digest(closure), sources=closure),
        native=dict(claim_wall_ns=str(claim_ns), event_wall_ns=str(event_ns), capture_wall_ns=str(capture_ns), elapsed_ns=time.monotonic_ns()-started,
            sequence=1, root_decision_ref=live['review'][2].decision_id, plan_artifact_ref=live['program'].topology_artifact.artifact_id,
            result_artifact_ref=live['artifact'].artifact_id, material_sha256=digest(material), output_sha256=digest(saved['output']), work_count=1,
            reached_boundary='WORK_ROOT', reason=None, time_envelope=saved['artifact']['time_envelope'], capture_ref=capture, semantic_ref=semantic, dependencies_sha256=digest(material)))
    source = feedback.NativeOutcomeSourceContextV01(canonical(native))
    proof = history.NativeOutcomeWorkProofV01(source=source, host=live['host'], program=live['program'], results=live['results'], common=live['common'],
        review_bindings=(), material=live['material'], review=live['review'])
    history.validate_native_work_proof_v01(proof)
    predictive = feedback.PredictiveOutcomeSourceContextV01(canonical(dict(profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID, native_source=native,
        claim_artifact=abi.kernel_artifact_to_plain_dict_v01(claim), result_artifact=saved['artifact'])))
    timestamp = int(time.time())
    observation = feedback.build_outcome_observation_v01(source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
        explicit_times=dict(ingested_time=timestamp, evaluated_at=timestamp, timestamp=timestamp))
    ofe = feedback.build_outcome_feedback_v01(observation=observation, source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    event = cal.bind_outcome_feedback_event_v01(ofe, source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    saved.update(predictive=json.loads(predictive.canonical), observation=json.loads(observation.canonical), feedback=json.loads(ofe.canonical),
        live_native_proof='VALIDATED_BEFORE_FEEDBACK', prospective_file_sha256=hashlib.sha256((directory/'prospective.json').read_bytes()).hexdigest())
    (directory/'observation.json').write_bytes(canonical(saved))
    return saved, event


def experience_v01(directory, bad_material, good_material):
    directory = Path(directory); catalogue = catalogue_v01()
    observed, event = observe_v01(directory/'native', bad_material, catalogue)
    store = history.OutcomeHistoryV01(directory/'history', trusted_events=(event,))
    snapshot, review = store.prepare_v01((json.loads(event.feedback_canonical)['feedback_id'],), expected_head=None, evaluated_at=int(time.time()))
    head = store.commit_v01(snapshot, review, expected_head=None)
    key = snapshot.to_plain_data()['prior']['history_key']
    before, _ = execute_current_v01(good_material, invocation='atlas:testflix:continuation', catalogue=catalogue_v01())
    after, live = execute_current_v01(good_material, invocation='atlas:testflix:continuation', catalogue=catalogue_v01(), store=store, history_key=key)
    require(before['projection']['selected'] != after['projection']['selected'], 'atlas_testflix_history_no_work_change')
    require(after['output']['checks'][0]['healthy'], 'atlas_testflix_continuation_not_eligible')
    return dict(observation=observed, snapshot=snapshot.to_plain_data(), recording_review=feedback.g35_record_to_plain_v01(review), head=head,
        storage=storage_projection_v01(directory/'history', (snapshot.to_plain_data(),)), before=before, after=after,
        counts=dict(native_observations=1, current_work_baselines=1, current_experience_consumers=1, new_provider_calls=0, payment_effects=0)), live
