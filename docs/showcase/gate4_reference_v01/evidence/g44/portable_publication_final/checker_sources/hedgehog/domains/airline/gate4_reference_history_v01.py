"""G42 glue for one prospective native observation and the existing G3 store.

No substitute learner, serialized Host reconstruction or action permission.
"""
import hashlib
import json
from pathlib import Path
import time

from hedgehog import outcome_feedback_v01 as feedback
from hedgehog import outcome_feedback_history_v01 as history
from hedgehog import outcome_calibration_v01 as calibration
from hedgehog.kernel import abi_v01 as abi


def keys_v01(config, constraints):
    from . import gate4_reference_adapter_v01 as a
    policy_ref='g42:prediction_policy:'+a.digest_v01(dict(constraints=a.plain_v01(constraints),configuration=config))
    revision=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    context=dict(local_root_scope_id=a.ROOT,domain='AIRLINE',pack_family_id='REVOCABLE_ACTION',
        advisory_source_class='G42_CONTROLLED_CONSTRAINT_PREDICTION',advisory_source_revision=revision,
        advice_claim_profile_id=feedback.PREDICTIVE_SOURCE_PROFILE_ID,route_family_id='PURE_AIRLINE_CONSTRAINT',
        task_risk_class='INFORMATIONAL',validation_profile_id='G34_TYPED_BOOLEAN_COMPLETED_WORK_V01',
        policy_semantics_version=policy_ref,history_key_profile_id='G3_TYPED_HISTORY_KEY_V01',
        task_class_id='AIRLINE_CONSTRAINT_CHECK',capability_contract_version='atlas.airline.constraint.v01')
    key=dict(local_root_scope_id=a.ROOT,domain_scope_id='AIRLINE',pack_family_id=context['pack_family_id'],
        route_family_id=context['route_family_id'],task_class_id=context['task_class_id'],task_risk_class=context['task_risk_class'],
        policy_semantics_version=policy_ref,capability_contract_version=context['capability_contract_version'],
        evidence_validation_profile_id=context['validation_profile_id'],advisory_source_revision=revision,
        history_key_profile_id=context['history_key_profile_id'])
    return context,key,policy_ref


def claim_v01(live):
    from . import gate4_reference_adapter_v01 as a
    material=live['initial_material']; now=live['claim_ns']//10**9
    prediction=dict(profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,predicted=live['config']['prediction']['predicted'],expected_fp=live['config']['prediction']['expected_fp'],
        claim_wall_ns=str(live['claim_ns']),dependencies_sha256=a.digest_v01(material),semantic_ref=live['semantic_ref'],
        operation='AIRLINE_CONSTRAINT_CHECK',source_observation_refs=[material['checks'][0]['observations'][0]['observation_id']],
        policy_ref=live['history_policy'],valid_from=now,valid_to=now+900,sequence=1)
    return abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:prediction:'+a.digest_v01(prediction),
        artifact_type='SemanticEvidence',schema_version='v1',transaction_id=live['transaction'],owner_root_id=a.ROOT,
        source_component='g42_prospective_source',authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',
        payload=prediction,trace_refs=(live['semantic_ref'],),parent_refs=(),time_envelope=live['env'])


def observe_v01(live,journal):
    from . import gate4_reference_adapter_v01 as a
    program,results,common=live['initial_program'],live['initial_results'],live['common']
    ok,reasons=a.work.validate_work_program_result_v01(program,results,**common,host_map={a.ROOT:live['host']})
    a.require_v01(ok,'g42_observation_work:'+repr(reasons))
    artifact=live['initial_artifact']; output=live['initial_output']; material=live['initial_material']
    review=a.informational_review_v42(live)
    capture_ns=time.time_ns(); now=live['claim_ns']//10**9
    closure={Path(m.__file__).name:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
        for m in (a,a.checks,a.binding,a.hosts,a.work,a.roots,a.semantic,abi,feedback,history,calibration)}
    closure[Path(__file__).name]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    ctx=dict(live['history_context'],source_id='g42:context:'+a.digest_v01(material),transaction_id=live['transaction'],
        run_id=live['task_id'],episode_id=live['task_id'],scenario_id='G42_NATIVE_AIRLINE_COMPARISONS')
    operation=dict(operation='AIRLINE_CONSTRAINT_CHECK',object_id=material['checks'][0]['offer_id'],recipient=a.ROOT)
    prediction=a.plain_v01(live['claim'])['payload']; occurrence='g42:occurrence:'+a.digest_v01(prediction)
    capture='g42:capture:'+a.digest_v01(artifact); origin='g42:origin:'+live['task_id']
    native=dict(source_profile_id=feedback.NATIVE_SOURCE_PROFILE_ID,evidence_class='NATIVE_CONTROLLED_OBSERVATION',context=ctx,
        policy=dict(source_id=live['history_policy'],revision=live['history_policy'],**operation),
        origin=dict(source_id=origin,occurrence_id=occurrence),
        proposal=dict(source_id=live['semantic_ref'],origin_ref=origin,created_at=now,recommendation='PROCEED',**operation),
        expectation=dict(source_id=live['claim'].artifact_id,created_at=now,expected_fp=prediction['expected_fp']),
        observation=dict(source_id=capture,proposal_ref=live['semantic_ref'],occurrence_ref=occurrence,**operation,
            result_revision=ctx['capability_contract_version'],event_time=live['event_ns']//10**9,
            boundary_disposition='PERMITTED',effect_count=0,result_state='PRESENT',failure='NONE'),
        closure=dict(source_id='g42:closure:'+a.digest_v01(closure),sources=closure),
        native=dict(claim_wall_ns=str(live['claim_ns']),event_wall_ns=str(live['event_ns']),capture_wall_ns=str(capture_ns),
            elapsed_ns=live['event_ns']-live['claim_ns'],sequence=1,root_decision_ref=review[2].decision_id,
            plan_artifact_ref=program.topology_artifact.artifact_id,result_artifact_ref=artifact.artifact_id,
            material_sha256=a.digest_v01(material),output_sha256=a.digest_v01(output),work_count=1,reached_boundary='WORK_ROOT',reason=None,
            time_envelope=a.plain_v01(artifact)['time_envelope'],capture_ref=capture,semantic_ref=live['semantic_ref'],dependencies_sha256=a.digest_v01(material)))
    source=feedback.NativeOutcomeSourceContextV01(a.canonical_v01(native))
    proof=history.NativeOutcomeWorkProofV01(source,live['host'],program,results,common,(),a.canonical_v01(material),review)
    history.validate_native_work_proof_v01(proof)
    predictive=feedback.PredictiveOutcomeSourceContextV01(a.canonical_v01(dict(profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
        native_source=native,claim_artifact=a.plain_v01(live['claim']),result_artifact=a.plain_v01(artifact))))
    timestamp=int(time.time())
    observation=feedback.build_outcome_observation_v01(source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
        explicit_times=dict(ingested_time=timestamp,evaluated_at=timestamp,timestamp=timestamp))
    ofe=feedback.build_outcome_feedback_v01(observation=observation,source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    a.require_v01(not feedback.validate_outcome_feedback_against_sources_v01(ofe,source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID),'g42_predictive_supplied')
    event=calibration.bind_outcome_feedback_event_v01(ofe,source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    f=json.loads(ofe.canonical)
    a.require_v01(f['avf_history_key']==live['history_key'],'g42_prospective_history_key')
    journal.save('observed_g3.json',dict(native=native,review=review,claim=live['claim'],artifact=artifact,
        predictive=json.loads(predictive.canonical),observation=json.loads(observation.canonical),feedback=f,live_proof='PASS',
        root_records=[feedback.g35_record_to_plain_v01(x) for x in review]))
    return event,proof


def consume_opened_v01(live,opened):
    from . import gate4_reference_adapter_v01 as a
    a.require_v01(opened is not None,'g42_required_history_missing')
    a.require_v01(opened['history_key']==live['history_key'],'g42_history_key_changed')
    bridge=opened['bridge']
    a.require_v01(bridge.owner_root_id==a.ROOT and bridge.transaction_id==live['transaction'],'g42_history_current_identity')
    a.require_v01(opened['evaluation_time']==live['clock'].evaluation_time,'g42_history_current_time')
    live['store'].validate_opened_v01(opened,bridge=bridge,evaluation_time=live['clock'].evaluation_time)
    now=live['task_clock'].now_v01(live['task_id'])
    a.require_v01(now>=opened['evaluation_time'],'g43_history_future_context')
    end=int(a.datetime.fromisoformat(a.plain_v01(bridge)['time_envelope']['valid_to']).timestamp())
    a.require_v01(now<end,'g43_current_history_expired')
    if now!=opened['evaluation_time']:
        current=live.get('current_opened')
        if current is None or current['evaluation_time']!=now:
            current,evidence=live['store'].current_v01(history_key=live['history_key'],root=a.ROOT,
                transaction=live['transaction'],evaluation_time=now)
            a.require_v01(current is not None,'g43_current_history_unavailable')
            a.require_v01(current['head']==opened['head'] and current['prior']==opened['prior']
                and current['payload_sha256']==opened['payload_sha256'],'g43_history_replan_required')
            live['current_opened']=current
            live.setdefault('current_history_evidence',[]).append(evidence)
        live['store'].validate_opened_v01(current,bridge=current['bridge'],evaluation_time=now)
    return opened['prior']['prior_fp']
