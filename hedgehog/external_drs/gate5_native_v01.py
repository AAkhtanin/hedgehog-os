"""G5-1 public-native adapters derived from recorded G5-0; no kernel copies."""
import dataclasses
import hashlib
import inspect
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from hedgehog.kernel import root_decision_v01 as roots
from hedgehog.kernel import semantic_work_v01 as sw, trust_model_v01 as trust
from hedgehog.kernel import work_composition_v01 as work, abi_v01 as abi
from hedgehog import action_commit_packet_v02 as action
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog import work_execution_host_v01 as hosts
from demo import run_action_packet_portability_v01 as donor
from demo import work_composition_mock_capabilities_v01 as mocks


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def plain(value):
    if dataclasses.is_dataclass(value):
        return {f.name: plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    if value is None or type(value) in (str, int, bool, float):
        return value
    raise TypeError(type(value).__name__)


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(json.dumps(value, sort_keys=True, indent=2).encode() + b'\n')


def root_review(root, transaction, candidate, subject, checks, claim_value, now,
                predicate='g51_bounded_context_review', window=None):
    """Actual public Root decision over locally computed predicates, not JSON permission."""
    assert checks and all(type(v) is bool for v in checks.values())
    evidence = 'evidence:g51:' + digest(dict(checks=checks, value=claim_value))
    req = sw.build_semantic_work_request_v01(request_id='review:' + candidate,
        transaction_id=transaction, target_root_id=root, runtime_topology_ref='g51:topology',
        bounded_context_refs=(evidence,), permitted_actor_ids=('g51:validator',),
        permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(subject,),
        required_evidence_classes=('DEPENDENCY_EVIDENCE',), forbidden_claims=('authority_creation',))
    ev = sw.build_evidence_binding_v01(evidence_id='binding:' + evidence, evidence_ref=evidence,
        evidence_class='DEPENDENCY_EVIDENCE', source_component_id='g51:validator',
        provenance_ref='g51:controlled_probe', evidence_state='PRESENT')
    claim = sw.build_normalized_claim_v01(claim_id=candidate, subject=subject, predicate=predicate,
        object_or_value=claim_value, time_envelope_ref='g51:time:' + str(now), provenance_refs=(evidence,),
        evidence_refs=(ev.evidence_id,), confidence_micros=1000000,
        source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    contribution = sw.build_actor_contribution_v01(contribution_id='contribution:' + candidate,
        request_id=req.request_id, actor_id='g51:validator', actor_role='deterministic_runtime',
        contribution_mode='DETERMINISTIC', bsep_projection_ref='g51:bsep', scope=subject,
        bounded_context_refs=(evidence,), claims=(claim,), evidence_bindings=(ev,),
        constraint_bindings=(), uncertainty_bindings=(), requested_validators=tuple(sorted(checks)),
        forbidden_claims_observed=())
    packet = sw.build_root_review_packet_from_contributions_v01(request=req, contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    actual_now = int(time.time())
    lower, upper = (now, now + 60) if window is None else window
    temporal_valid = lower <= actual_now < upper and now <= actual_now
    valid = all(checks.values()) and temporal_valid
    kernel = roots.build_root_decision_kernel_v01()
    inputs = roots.build_root_decision_input_v01(transaction_id=transaction, target_root_id=root,
        root_review_packet=packet,
        post_vv_bundle=dict(bundle_id='g51:checks:' + digest(checks), post_vv_passed=valid,
            validated_candidate_ids=[candidate] if valid else [], rejected_candidate_ids=[] if valid else [candidate],
            required_evidence_refs=[evidence], provided_evidence_refs=[evidence],
            hard_failure_reasons=[] if valid else ['policy_validation_failed']),
        gt_advisory=dict(advisory_id='gt:' + candidate, candidate_ids=[candidate],
            selected_candidate_id=candidate if valid else None, score_micros_by_candidate={candidate:1000000 if valid else 0},
            source_artifact_type='GTAdvisoryReport', source_lifecycle_state='VALIDATED', actor_role='gt',
            attempted_effect='CREATE_ROOT_DECISION', target_artifact_type='RootDecision', advisory_only=True,
            creates_final_output=False, requests_effect=False),
        policy_state=dict(policy_id='g51:operator_pinned', identity_passed=valid, scope_passed=valid,
            hard_policy_passed=valid, allow_accept=valid, conflict_policy='DEFER', no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=False, user_permission_present=False,
            permission_scope_valid=valid, permission_ref=None),
        temporal_state=dict(temporal_valid=temporal_valid, expired=actual_now >= upper, not_before_satisfied=actual_now >= lower,
            time_envelope_ref='g51:time:' + str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids), conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None, prior_decision=None, prior_selected_candidate_id=None))
    result = roots.decide_root_v01(kernel=kernel, decision_input=inputs)
    assert not roots.validate_root_decision_result_v01(kernel=kernel, decision_input=inputs, result=result)
    assert (result.decision == 'ACCEPT') == valid
    return kernel, inputs, result


def root_plain(review):
    return dict(kernel=plain(review[0]), inputs=plain(review[1]), result=roots.root_decision_result_to_plain_dict_v01(review[2]))


def rebuilt(builder, data):
    signature = inspect.signature(builder)
    values = {k: tuple(v) if isinstance(v, list) else v for k, v in data.items() if k in signature.parameters}
    return builder(**values)


def pointer_descent_v01(pointer, folder, source_end):
    from hedgehog.drs import LocalDRS
    from hedgehog import local_drs_resolver as resolver, drs_semantic_address_v01 as address, drs_memory_resolution_v01 as memory
    from hedgehog.kernel import integrity_replay_v01 as integrity
    start = time.monotonic()
    now = int(time.time())
    assert now < source_end
    ttl = source_end - now
    assert set(pointer) == {'publisher', 'source_record', 'revision', 'pointer_id', 'body_sha256', 'schema', 'endpoint_ref'}
    # Human summary is semantic metadata, not a JSON dump of opaque digests.
    # Exact descriptor identity remains in the record's content fingerprint.
    summary = canonical({k: v for k, v in pointer.items() if k not in ('pointer_id', 'body_sha256')}).decode()
    policy, domain = 'g51.pointer.context.v01', 'G51_POINTER'
    addr = address.build_semantic_address_v01(namespace='g51', domain=domain, subject_class='external_pointer',
        intent_class='context_lookup', meaning_schema_id='g51.pointer_metadata', meaning_schema_version='v01')
    env = address.build_drs_time_envelope_v01(pt_created_at=now, kt_as_of=now, et_observed_at=now, ct_context_anchor=now,
        ttl_seconds=ttl, valid_from=now, valid_to=source_end, source_observed_at=now, source_reported_at=now,
        system_ingested_at=now, system_verified_at=now, freshness_policy_id='freshness:g51:pointer')
    review = root_review('root:gate5:site', 'transaction:g51:pointer', 'candidate:g51:pointer', addr.semantic_address_id,
        dict(metadata_only=True, pinned_publisher=pointer['publisher']=='root:gate5:calibration'), pointer, now)
    records = []
    drs = LocalDRS(folder / 'drs')
    for accepted in (False, True):
        auth = address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_CONTEXT' if accepted else 'CONNECTOR_OBSERVATION',
            owning_local_root_id='root:gate5:site' if accepted else None,
            source_root_decision_input_id=review[1].decision_input_id if accepted else None,
            source_root_decision_id=review[2].decision_id if accepted else None,
            source_root_decision_hash=digest(roots.root_decision_result_to_plain_dict_v01(review[2])) if accepted else None,
            authority_scope_fingerprint=digest(pointer),
            root_acceptance_state='ACCEPTED_CONTEXT' if accepted else 'UNREVIEWED', recording_component='g51:connector')
        record = address.build_meaning_record_v01(semantic_address=addr, predecessor_record_id=None, supersession_reason=None,
            safe_summary=summary, semantic_tags=('g51', 'pointer'), resonance_reason='Foreign pointer only; never action permission.',
            memory_pointers=(), artifact_pointers=(), source_reference_ids=(pointer['source_record'],), lineage_edges=(),
            time_envelope=env, authority_envelope=auth, persistent_lifecycle_state='ACTIVE', risk_hints=(), conflict_hints=(),
            reuse_policy_class='CONTEXT_ONLY', policy_version=policy, schema_versions=(policy,), content_fingerprint=digest(pointer), recording_component='g51:connector')
        stamp = lambda x: datetime.fromtimestamp(x, timezone.utc).isoformat()
        resolver.write_semantic_record(drs, resolver.SemanticDRSRecordInput(record_id=record.meaning_record_id, domain=domain,
            content=dict(kind='pointer', record=address.meaning_record_to_plain_data_v01(record)), semantic_keys=('g51', 'pointer'),
            time_envelope=dict(pt_created_at=stamp(now), kt_asof=stamp(now), et_observed_at=stamp(now), ct_session_anchor='g51:session',
                ttl_seconds=ttl, freshness_class='static', valid_from=stamp(now), valid_to=stamp(source_end))))
        records.append(record.meaning_record_id)
    # A new instance reads persisted bytes. No in-memory meaning-record registry is used.
    drs = LocalDRS(folder / 'drs')
    resolved = resolver.resolve_semantic_candidates(drs, resolver.SemanticResolveQuery(query_id='g51:lookup', domain=domain,
        semantic_terms=('g51','pointer'), content_filters=dict(kind='pointer'), require_root_review=True), layers=('work',))
    assert set(records) == {c.record_id for c in resolved.candidates}
    evaluations = []
    for record_id in records:
        stored = drs.read_record('work', record_id)['content']['record']
        source = dict(stored, semantic_address=rebuilt(address.build_semantic_address_v01, stored['semantic_address']),
            time_envelope=rebuilt(address.build_drs_time_envelope_v01, stored['time_envelope']),
            authority_envelope=rebuilt(address.build_drs_authority_envelope_v01, stored['authority_envelope']))
        record = rebuilt(address.build_meaning_record_v01, source)
        assert address.meaning_record_to_plain_data_v01(record) == stored
        query = memory.build_drs_temporal_query_v01(query_mode='CURRENT_DECISION', semantic_address_id=addr.semantic_address_id,
            scope_fingerprint=digest(pointer), as_of=now, evaluation_time=now, evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',
            time_range_start=now, time_range_end=now+1, required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),
            freshness_policy_id=env.freshness_policy_id, max_age_seconds=ttl, domain=domain, risk_class='LOW', reuse_intent='CONTEXT',
            requested_reuse_classes=('CONTEXT_ONLY',), required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN',
                'TIME_FITNESS','POLICY_COMPATIBILITY','SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),
            forbidden_changes=('POLICY_CHANGED',), policy_version=policy, schema_versions=(policy,), owning_local_root_id='root:gate5:site')
        evaluation = memory.evaluate_drs_candidate_v01(semantic_address=addr, query=query, meaning_record=record)
        evaluations.append(memory.query_evaluation_state_to_plain_data_v01(evaluation))
    assert not evaluations[0]['eligible_for_ranking'] and evaluations[1]['eligible_for_ranking']
    budget = memory.build_memory_descent_budget_v01(max_depth=0,max_records_opened=1,max_pointers_opened=0,max_artifacts_opened=0,
        max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
    plan = memory.build_retrieval_plan_v01(query_id=query.query_id, semantic_address_id=addr.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),
        requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(),reason_codes=())
    review = root_review('root:gate5:site',query.query_id,plan.retrieval_plan_id,addr.semantic_address_id,
        dict(eligible=evaluation.eligible_for_ranking,pointer_only=True),memory.retrieval_plan_to_plain_data_v01(plan),now,
        predicate='approve_controlled_memory_descent_plan_v01')
    rh = integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
        payload=canonical(roots.root_decision_result_to_plain_dict_v01(review[2])))
    request = memory.build_memory_descent_request_v01(retrieval_plan_id=plan.retrieval_plan_id,query_id=query.query_id,
        owning_local_root_id='root:gate5:site',root_kernel_id=review[0].kernel_id,root_decision_input_id=review[1].decision_input_id,
        root_decision_id=review[2].decision_id,root_decision_hash=rh,requested_descent_class='SUMMARY_ONLY',approved_descent_class='SUMMARY_ONLY',
        proposed_budget_id=budget.memory_descent_budget_id,approved_budget=budget,approved_record_ids=(record.meaning_record_id,),
        approved_memory_pointer_ids=(),approved_artifact_pointer_ids=())
    result = memory.execute_local_memory_descent_v01(retrieval_plan=plan,proposed_budget=budget,descent_request=request,
        root_kernel=review[0],root_decision_input=review[1],root_decision_result=review[2],source_records=(record,))
    assert result.limits_respected and not result.reason_codes and result.safe_summaries == (summary,)
    assert record.content_fingerprint == digest(pointer)
    report = dict(pointer=pointer, resolver=plain(resolved), evaluations=evaluations, root=root_plain(review),
        descent=memory.memory_descent_result_to_plain_data_v01(result), seconds=time.monotonic()-start)
    save(folder / 'pointer_descent.json', report)
    return report


from . import gate5_contracts_v01 as c


def compute_values(mode, values):
    readings = c.decode(values['readings'].encode())
    if mode == 'source':
        result = c.calibration(values['reference'], readings)
        return dict(correction_den=result['correction']['den'], correction_num=result['correction']['num'],
            n=result['n'], total=result['total'])
    mean = c.rational(c.total(readings), len(readings))
    if mode == 'mean':
        return dict(mean_den=mean['den'], mean_num=mean['num'])
    result = c.corrected(readings, dict(num=values['offset_num'], den=values['offset_den']))
    return dict(corrected_den=result['corrected']['den'], corrected_num=result['corrected']['num'],
        mean_den=result['mean']['den'], mean_num=result['mean']['num'])


def execute_calibration_v01(invocation):
    return execute_values('source', invocation)


def execute_mean_v01(invocation):
    return execute_values('mean', invocation)


def execute_corrected_v01(invocation):
    return execute_values('corrected', invocation)


def execute_values(mode, invocation):
    values = {v.parameter_name:v.value for v in invocation.inputs}
    result = compute_values(mode, values)
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=k,value_type='INTEGER',value=v) for k,v in sorted(result.items()))


def validate_math_output_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    mode = definition.operation_id.split('.')[-1]
    if not errors and {v.parameter_name:v.value for v in output} != compute_values(mode,{v.parameter_name:v.value for v in invocation.inputs}):
        errors = ('gate5_math_result_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,
        invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)


def native_work(mode, root, task, values):
    started = time.monotonic()
    executor = {'source':execute_calibration_v01,'mean':execute_mean_v01,'corrected':execute_corrected_v01}[mode]
    input_fields = tuple((k,'TEXT' if k=='readings' else 'INTEGER') for k in sorted(values))
    required = {'source':{'readings','reference'},'mean':{'readings'},'corrected':{'readings','offset_den','offset_num'}}[mode]
    c.require(set(values)==required, 'native_required_inputs')
    output_fields = {'source':('correction_den','correction_num','n','total'),'mean':('mean_den','mean_num'),
        'corrected':('corrected_den','corrected_num','mean_den','mean_num')}[mode]
    admission = mocks.admit_pure_operation_v01(operation_id='gate5.'+mode, input_fields=input_fields,
        output_fields=tuple((k,'INTEGER') for k in output_fields),executor=executor,
        output_validator=validate_math_output_v01,host_instance_ref='host:'+root)
    item = work.WorkItemV01(mode,admission.definition.definition_id,root,
        tuple(donor.work_literal_v01(k,t,values[k]) for k,t in input_fields),(),(),None,None)
    program,common,host = donor.prepare_work_program_v01(task_id=task,root_id=root,admitted=(admission,),items=(item,),device_refs=())
    results = work.advance_work_program_v01(program,**common,host_map={root:host})
    valid,reasons = work.validate_work_program_result_v01(program,results,**common,host_map={root:host})
    c.require(valid and not reasons and len(results)==1 and results[0].status=='COMPLETED','native_work_failed')
    artifact = work.work_program_result_to_artifact_v01(program,results,**common,host_map={root:host})
    result = {v.parameter_name:v.value for v in results[0].result.output}
    snapshot = firewall.snapshot_admitted_capability_v01(admission)
    c.require(not firewall.validate_capability_execution_result_v01(results[0].result,results[0].invocation,snapshot),'pure_result_validation')
    native_evidence = dict(admission=plain(snapshot),invocation=plain(results[0].invocation),result=plain(results[0].result))
    return dict(mode=mode,task=task,root=root,inputs=values,outputs=result,results=plain(results),
        artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),native_evidence=native_evidence,attempts=len(host.work_attempts),
        seconds=time.monotonic()-started,clock_profile='ADMITTED_CONTROLLED_WORK_DONOR_LOGICAL_1014_PROTOCOL_SOURCE_UTC_SEPARATE')


def persist_and_resolve_pointer(envelope, folder, policy):
    from hedgehog.drs import LocalDRS
    from hedgehog import local_drs_resolver as resolver
    pointer = envelope['value']
    drs = LocalDRS(folder/'address_index')
    resolver.write_semantic_record(drs,resolver.SemanticDRSRecordInput(record_id=pointer['pointer_id'],domain='G51_DESCRIPTOR',
        content=dict(kind='signed_pointer',descriptor=envelope),semantic_keys=('calibration','pointer')))
    # Lookup begins with persisted state, never with a process-global pointer registry.
    drs = LocalDRS(folder/'address_index')
    report = resolver.resolve_semantic_candidates(drs,resolver.SemanticResolveQuery(query_id='query:gate5:descriptor',
        domain='G51_DESCRIPTOR',semantic_terms=('calibration','pointer'),require_root_review=True),layers=('work',))
    c.require(len(report.candidates)==1,'pointer_resolution')
    stored = drs.read_record('work',report.candidates[0].record_id)['content']['descriptor']
    p = stored['value']
    metadata = dict(publisher=p['publisher_root_id'],source_record=p['source_record_ref'],revision=p['source_revision'],
        pointer_id=p['pointer_id'],body_sha256=p['body_sha256'],schema=p['semantic_address']['schema_id'],endpoint_ref='endpoint:gate5:A')
    descent = pointer_descent_v01(metadata,folder/'local_descent',c.temporal(p['time_envelope'],int(time.time()),policy))
    c.require(descent['pointer']==metadata,'descent_pointer_binding')
    save(folder/'descriptor_resolution.json',dict(resolver=plain(report),persisted_pointer_hash=c.sha(stored),descent_root=descent['root']['result']['decision_id']))
    return stored
