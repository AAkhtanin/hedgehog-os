"""Bounded native observation store. JSON reports never reconstruct live authority."""
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import time

from hedgehog import outcome_feedback_v01 as feedback
from hedgehog.kernel import abi_v01 as abi, root_decision_v01 as roots
from . import contracts_v01 as c, kernel_adapter_v01 as kernel
from .evidence_v01 import plain

CLAIM_PROFILE = 'G32_CURRENT_ROLE_FAITHFUL_OUTPUT_V01'


def _hash(value):
    return hashlib.sha256(c.canonical(value)).hexdigest()


def _closure():
    root=Path(__file__).resolve().parents[2]
    paths=('domains/landslide_sentinel/outcome_feedback_adapter_v01.py',
        'domains/landslide_sentinel/monitoring_runtime_v01.py','domains/landslide_sentinel/kernel_adapter_v01.py',
        'domains/landslide_sentinel/semantic_adapter_v01.py','domains/landslide_sentinel/capability_registry_v01.py',
        'domains/landslide_sentinel/contracts_v01.py','kernel/work_composition_v01.py',
        'kernel/root_decision_v01.py','work_execution_host_v01.py','outcome_feedback_v01.py')
    return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in paths}


@dataclass(frozen=True, slots=True)
class SentinelOutcomeCaptureV01:
    capture_id: str
    source_canonical: bytes
    native_canonical: bytes
    ordinal: int
    _origin: object = field(repr=False,compare=False)


class SentinelOutcomeSourceV01:
    """One trusted application-owned episode; at most four observed attempts.

    This object is supplied separately by the local application, not parsed from
    feedback. Every use checks actual origin, retained bytes and native evidence.
    """
    def __init__(self, session):
        self.session=session
        self._records={}
        self._origin=object()

    def observe_role_v01(self, semantic, *, expected_fp):
        c.require(len(self._records)<4,'g32_observation_cap')
        c.require(expected_fp is None or type(expected_fp) is int and 0<=expected_fp<=feedback.Q,'g32_expectation')
        c.require(semantic['profile']=='CONTROLLED_ROLE_FIXTURE' and semantic['actual_mode']=='DETERMINISTIC'
            and semantic['response']['diagnostic']=='REFERENCE_INTEGRITY','g32_bounded_role')
        semantic=json.loads(c.canonical(semantic))
        session=self.session
        ordinal=len(self._records)+1
        claim_ns=time.time_ns()
        claim=dict(profile=CLAIM_PROFILE,root=session.root,task=session.id,operation='REFERENCE_INTEGRITY',
            object_ref=session.fixture['site'],semantic_sha256=_hash(semantic),dependencies_sha256=hashlib.sha256(kernel.work_dependencies(session)).hexdigest(),
            expected_fp=expected_fp,wall_ns=str(claim_ns),sequence=ordinal*2,source_closure=_closure(),effects_before=len(session.executed),
            claim='Current role/source suitability and faithful public diagnostic output; no geological safety assertion')
        claim_id='g32:claim:'+_hash(claim)
        # Persist the prospective input before the target public boundary.
        path=session.directory/('g32_prospective_'+str(ordinal)+'.json')
        path.write_bytes(c.canonical(dict(claim_id=claim_id,claim=claim,semantic=semantic))+b'\n')
        started=time.monotonic_ns()
        plan=result_basis=record=None
        reason=None
        try:
            plan,_=session.plan_roles([semantic],fractal=False)
        except ValueError as error:
            reason=str(error)
            # This profile records this inspected pre-work boundary only. A
            # later Work/Root failure must propagate, not masquerade as early.
            if reason!='role_current_root_policy':
                raise
        if plan is not None:
            record=session.execute_role_plan(plan)
            result_basis=session.reviewed_role_result(record['work_artifact']['artifact_id'])
            output=kernel.validate_reviewed_work(session,result_basis)
            c.require(output==record['output'],'g32_actual_consumed_output')
            c.require(output['stage']=='RESULT' and output['semantic_refs']==[semantic['contribution']['contribution_id']],'g32_role_consumption')
        else:
            c.require(reason is not None,'g32_missing_native_disposition')
        ended=time.time_ns();elapsed=time.monotonic_ns()-started
        native=dict(claim_id=claim_id,claim=claim,semantic=semantic,record=record,reason=reason,
            reached_boundary='WORK_ROOT' if result_basis else 'SEMANTIC_VALIDATION',
            event_wall_ns=str(ended),capture_wall_ns=str(time.time_ns()),elapsed_ns=elapsed,
            scenario_tick=session.tick,effect_count=len(session.executed)-claim['effects_before'],dependencies=kernel.work_dependencies(session).decode())
        if result_basis:
            native['result_root_input']=roots.root_decision_input_to_plain_dict_v01(result_basis.review[1])
            native['result_root']=roots.root_decision_result_to_plain_dict_v01(result_basis.review[2])
        capture_id='g32:capture:'+_hash(native)
        source=self._normalize(native,capture_id,ordinal,result_basis)
        capture=SentinelOutcomeCaptureV01(capture_id,feedback._canonical(source),c.canonical(native),ordinal,self._origin)
        self._records[capture_id]=(capture,plan,result_basis)
        return capture

    def _normalize(self,native,capture_id,ordinal,basis):
        session=self.session;claim=native['claim'];semantic=native['semantic']
        claim_sec=int(claim['wall_ns'])//10**9;event_sec=int(native['event_wall_ns'])//10**9
        ref=native['claim_id'];proposal=semantic['contribution']['contribution_id']
        policy_revision='policy:'+_hash(session.contract)
        capability_revision='capability:'+_hash(session.capabilities.snapshot(semantic['intended_role']))
        ctx=dict(source_id='g32:context:'+_hash(dict(root=session.root,task=session.id,dependencies=native['dependencies'])),
            local_root_scope_id=session.root,domain='LANDSLIDE_SENTINEL',pack_family_id='REVOCABLE_ACTION',
            advisory_source_class='CONTROLLED_DETERMINISTIC_ROLE',advisory_source_revision=claim['source_closure']['domains/landslide_sentinel/semantic_adapter_v01.py'],
            advice_claim_profile_id=CLAIM_PROFILE,route_family_id='PURE_REFERENCE_INTEGRITY',task_risk_class='INFORMATIONAL',
            validation_profile_id='G32_NATIVE_PUBLIC_WORK_ROOT_V01',policy_semantics_version=policy_revision,
            history_key_profile_id='G3_TYPED_HISTORY_KEY_V01',task_class_id='REFERENCE_INTEGRITY',capability_contract_version=capability_revision,
            transaction_id='transaction:'+session.id,run_id=session.id,episode_id=session.id,scenario_id='NATIVE_ROLE_OBSERVATION')
        operation=dict(operation='REFERENCE_INTEGRITY',object_id=claim['object_ref'],recipient=session.root)
        reached=basis is not None
        env=abi.kernel_artifact_to_plain_dict_v01(basis.artifact)['time_envelope'] if reached else dict(
            pt_created_at=feedback._utc(event_sec),kt_asof=feedback._utc(claim_sec),et_observed_at=feedback._utc(event_sec),
            ct_session_anchor=session.id,ttl_seconds=3600,freshness_class='static',valid_from=feedback._utc(claim_sec),valid_to=feedback._utc(event_sec+3600))
        occurrence='g32:occurrence:'+_hash(dict(claim_id=ref,ordinal=ordinal,task=session.id))
        return dict(source_profile_id=feedback.NATIVE_SOURCE_PROFILE_ID,evidence_class='NATIVE_CONTROLLED_OBSERVATION',context=ctx,
            policy=dict(source_id=policy_revision,revision=policy_revision,**operation),
            origin=dict(source_id='g32:origin:'+_hash(semantic),occurrence_id=occurrence),
            proposal=dict(source_id=proposal,origin_ref='g32:origin:'+_hash(semantic),created_at=claim_sec,recommendation='PROCEED',**operation),
            expectation=dict(source_id=ref,created_at=claim_sec,expected_fp=claim['expected_fp']),
            observation=dict(source_id=capture_id,proposal_ref=proposal,occurrence_ref=occurrence,**operation,
                result_revision=capability_revision,event_time=event_sec,boundary_disposition='PERMITTED' if reached else 'NOT_OBSERVED',
                effect_count=native['effect_count'],result_state='PRESENT' if reached else 'MISSING',failure='NONE' if reached else 'OBSERVATION_INCOMPLETE'),
            closure=dict(source_id='g32:closure:'+_hash(claim['source_closure']),sources=claim['source_closure']),
            native=dict(claim_wall_ns=claim['wall_ns'],event_wall_ns=native['event_wall_ns'],capture_wall_ns=native['capture_wall_ns'],
                elapsed_ns=native['elapsed_ns'],sequence=ordinal*2+1,root_decision_ref=basis.review[2].decision_id if reached else None,
                plan_artifact_ref=native['record']['plan_basis']['work_artifact_ref'] if reached else None,
                result_artifact_ref=basis.artifact.artifact_id if reached else None,material_sha256=hashlib.sha256(basis.material).hexdigest() if reached else None,
                output_sha256=_hash(native['record']['output']) if reached else None,work_count=len(native['record']['results'])+len(native['record']['plan_results']) if reached else 0,
                reached_boundary=native['reached_boundary'],reason=native['reason'],time_envelope=env,capture_ref=capture_id,
                semantic_ref=proposal,dependencies_sha256=claim['dependencies_sha256']))

    def validate_capture_v01(self,capture,*,require_current=True):
        c.require(type(capture) is SentinelOutcomeCaptureV01 and capture._origin is self._origin,'g32_capture_origin')
        saved,plan,basis=self._records.get(capture.capture_id,(None,None,None))
        c.require(saved is not None and saved.source_canonical==capture.source_canonical and saved.native_canonical==capture.native_canonical
            and saved.ordinal==capture.ordinal,'g32_retained_capture')
        native=json.loads(capture.native_canonical)
        c.require(native['claim']['source_closure']==_closure(),'g32_source_closure_changed')
        c.require(capture.capture_id=='g32:capture:'+_hash(native),'g32_capture_content')
        c.require(native['claim']['root']==self.session.root and native['claim']['task']==self.session.id,'g32_source_owner')
        if basis is not None:
            c.require(self.session.reviewed_role_result(basis.artifact.artifact_id) is basis,'g32_retained_result_basis')
            if require_current:
                kernel.validate_reviewed_work(self.session,plan)
                output=kernel.validate_reviewed_work(self.session,basis)
                c.require(output==native['record']['output'],'g32_native_output_changed')
            for value,root_data,artifact_data in ((plan,native['record']['plan_root'],native['record']['plan_basis']),
                (basis,native['result_root'],native['record']['work_artifact'])):
                rk,ri,rr=value.review
                c.require(not roots.validate_root_decision_result_v01(kernel=rk,decision_input=ri,result=rr),'g32_saved_native_root')
                c.require(plain(rr)==root_data,'g32_saved_root_changed')
            c.require(abi.kernel_artifact_to_plain_dict_v01(basis.artifact)==native['record']['work_artifact']
                and plain(basis.results)==native['record']['results'] and json.loads(basis.material)==native['record']['material'],'g32_saved_native_changed')
        if require_current:
            c.require(native['dependencies']==kernel.work_dependencies(self.session).decode(),'g32_current_source_changed')
        return feedback.NativeOutcomeSourceContextV01(capture.source_canonical)

    def build_feedback_v01(self,capture,*,require_current=True):
        source=self.validate_capture_v01(capture,require_current=require_current)
        now=max(int(time.time()),int(json.loads(capture.native_canonical)['capture_wall_ns'])//10**9)
        observation=feedback.build_outcome_observation_v01(source_bundle=source,profile=feedback.NATIVE_SOURCE_PROFILE_ID,
            explicit_times=dict(ingested_time=now,evaluated_at=now,timestamp=now))
        return observation,feedback.build_outcome_feedback_v01(observation=observation,source_bundle=source,profile=feedback.NATIVE_SOURCE_PROFILE_ID)

    def validate_feedback_v01(self,value,*,capture,supplied_source=None,require_current=True):
        try:
            context=self.validate_capture_v01(capture,require_current=require_current)
            supplied=feedback.outcome_feedback_to_plain_data_v01(value)
            c.require(supplied['timestamp']<=time.time_ns()//10**9,'g32_future_evidence_time')
            if supplied_source is not None:
                c.require(feedback._canonical(supplied_source)==context.canonical,'g32_supplied_source_changed')
            return feedback.validate_outcome_feedback_against_sources_v01(value,source_bundle=context,profile=feedback.NATIVE_SOURCE_PROFILE_ID)
        except (ValueError,KeyError,TypeError) as error:
            return (str(error),)

    def native_basis_v01(self,capture):
        self.validate_capture_v01(capture)
        return self._records[capture.capture_id][2]


def collect_g35_source_v01(directory):
    """One actual diagnostic plus current/stale public observation suitability."""
    from .monitoring_runtime_v01 import ControlledEpisode
    from . import events_v01 as events, semantic_adapter_v01 as sem
    from hedgehog.kernel import effect_firewall_v01 as fw
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[3]
    fixture=json.loads((root/'fixtures/landslide_sentinel/ls1_inputs_v01.json').read_bytes())
    spec=json.loads((root/'fixtures/gate3_sentinel_observation_v01.json').read_bytes())
    session=ControlledEpisode(directory/'episode',fixture)
    observations=[events.observation(v['sensor'],v['value'],120,1) for v in fixture['frames']]
    session.ingest(observations,120)
    semantic=sem.collect(session.frames,fixture['maintenance_note'],session.root,session.source.sample().evaluation_time,
        controlled=spec['response'],intended_role=spec['role'],capabilities=session.capabilities.snapshot(spec['role']),
        observations=tuple(session.book.latest.values()),tick=session.tick,policy=session.contract)[1]
    store=SentinelOutcomeSourceV01(session);capture=store.observe_role_v01(semantic,expected_fp=None)
    basis=store.native_basis_v01(capture)
    current=session.book.current('displacement','configuration')
    session.book.advance(301)
    try:session.book.current('displacement','configuration')
    except ValueError as exc:refusal=str(exc)
    else:raise ValueError('g35_stale_observation_accepted')
    body=dict(source=json.loads(capture.source_canonical),native=json.loads(capture.native_canonical),
        root=[feedback.g35_record_to_plain_v01(v) for v in basis.review],
        work=feedback.g35_record_to_plain_v01(basis.results),
        admissions=feedback.g35_record_to_plain_v01(tuple(fw.snapshot_admitted_capability_v01(v) for v in basis.common['catalogue'])),
        current=current,stale_tick=session.book.tick,stale_refusal=refusal,effects=len(session.executed))
    return body


def validate_g35_source_v01(body):
    """Pure saved data/Root validation; no episode, Host, DRS or new decision."""
    from . import events_v01 as events, capability_registry_v01 as caps
    feedback._keys(body,('source','native','root','work','admissions','current','stale_tick','stale_refusal','effects'))
    context=feedback.NativeOutcomeSourceContextV01(feedback._canonical(body['source']))
    source,_=feedback._source(context,feedback.NATIVE_SOURCE_PROFILE_ID)
    native=body['native'];ref='g32:capture:'+_hash(native)
    feedback._require(source['native']['capture_ref']==ref and body['effects']==0 and native['effect_count']==0,'g35_sentinel_capture')
    inputs,result=feedback.g35_validate_root_v01(body['root'])
    artifact=feedback.g35_validate_artifact_v01(native['record']['work_artifact'])
    rows=feedback.g35_validate_work_records_v01(body['work'],body['admissions'])
    feedback._require(result.target_root_id==artifact.owner_root_id==source['context']['local_root_scope_id'] and
        result.transaction_id==artifact.transaction_id and result.decision=='ACCEPT','g35_sentinel_root')
    actual=json.loads(caps.values(rows[-1].result.output)['material'])
    feedback._require(actual==native['record']['output'] and plain(rows)==native['record']['results'] and
        source['native']['root_decision_ref']==result.decision_id and source['native']['result_artifact_ref']==artifact.artifact_id,'g35_sentinel_output')
    events.validate(body['current'])
    book=events.EventBook();book.ingest([body['current']],120)
    feedback._require(book.current('displacement','configuration')==body['current'],'g35_sentinel_current')
    book.advance(body['stale_tick'])
    try:book.current('displacement','configuration')
    except ValueError as exc:feedback._require(str(exc)==body['stale_refusal']=='measurement_stale_for_configuration','g35_sentinel_stale_reason')
    else:raise ValueError('g35_sentinel_stale_not_refused')
    common=dict(root=result.target_root_id,transaction=result.transaction_id,proposal=source['proposal']['source_id'])
    return [feedback.g35_fact_v01(**common,decision=result.decision_id,artifact=artifact.artifact_id,work_count=source['native']['work_count']),
        feedback.g35_fact_v01(**common,task='NEEDS_INPUT',enforcement='BLOCKED_AS_REQUIRED',execution='NEEDS_MORE_EVIDENCE',stage='CURRENTNESS')]


@dataclass(frozen=True, slots=True)
class PredictiveCaptureV01:
    source_canonical: bytes
    ordinal: int
    _origin: object = field(repr=False, compare=False)


class SentinelPredictiveSourceV01:
    """Finite, separate G34 stream on one stable Root; old G32 cap is unchanged."""
    def __init__(self, session):
        self.session = session
        self._origin = object()
        self._captures = []

    def observe_v01(self, semantic, *, predicted=True, expected_fp, validity_seconds=604800):
        c.require(len(self._captures) < 64 and type(predicted) is bool, 'g34_predictive_bound')
        c.require(type(validity_seconds) is int and 0 < validity_seconds <= 604800, 'g34_validity')
        session = self.session
        material = session.role_material(semantic)
        claim_ns = time.time_ns()
        now = claim_ns // 10**9
        payload = dict(profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID, predicted=predicted, expected_fp=expected_fp,
            claim_wall_ns=str(claim_ns), dependencies_sha256=hashlib.sha256(kernel.work_dependencies(session)).hexdigest(),
            semantic_ref=semantic['contribution']['contribution_id'], operation='REFERENCE_INTEGRITY',
            source_observation_refs=sorted(v['observation_id'] for v in material['checks'][0]['observations']),
            policy_ref='policy:'+_hash(session.contract), valid_from=now, valid_to=now+validity_seconds,
            sequence=len(self._captures)+1)
        envelope=dict(pt_created_at=feedback._utc(now), kt_asof=feedback._utc(now), et_observed_at=None,
            ct_session_anchor=session.id, ttl_seconds=validity_seconds, freshness_class='static',
            valid_from=feedback._utc(now), valid_to=feedback._utc(now+validity_seconds))
        claim = abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:prediction:'+_hash(payload),
            artifact_type='SemanticEvidence',schema_version='v1',transaction_id='transaction:'+session.id,
            owner_root_id=session.root,source_component='g34_predictive_source',authority_class='EVIDENCE_ONLY',
            lifecycle_state='VALIDATED',payload=payload,trace_refs=(payload['semantic_ref'],),parent_refs=(),time_envelope=envelope)
        (session.directory/('g34_prospective_'+str(payload['sequence'])+'.json')).write_bytes(
            c.canonical(abi.kernel_artifact_to_plain_dict_v01(claim)))
        native_store=SentinelOutcomeSourceV01(session)
        native_capture=native_store.observe_role_v01(semantic,expected_fp=expected_fp)
        source=native_store.validate_capture_v01(native_capture)
        basis=native_store.native_basis_v01(native_capture)
        context=feedback.PredictiveOutcomeSourceContextV01(c.canonical(dict(
            profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,native_source=json.loads(source.canonical),
            claim_artifact=abi.kernel_artifact_to_plain_dict_v01(claim),
            result_artifact=abi.kernel_artifact_to_plain_dict_v01(basis.artifact))))
        capture=PredictiveCaptureV01(context.canonical,payload['sequence'],self._origin)
        (session.directory/('g34_native_'+str(payload['sequence'])+'.json')).write_bytes(native_capture.native_canonical)
        self._captures.append((capture,native_store,native_capture))
        return capture

    def validate_capture_v01(self,capture,*,require_current=False):
        c.require(type(capture) is PredictiveCaptureV01 and capture._origin is self._origin,'g34_capture_origin')
        c.require(1<=capture.ordinal<=len(self._captures),'g34_capture_ordinal')
        saved,store,native=self._captures[capture.ordinal-1]
        c.require(saved.source_canonical==capture.source_canonical,'g34_capture_content')
        context=store.validate_capture_v01(native,require_current=require_current)
        c.require(json.loads(capture.source_canonical)['native_source']==json.loads(context.canonical),'g34_native_source_changed')
        return feedback.PredictiveOutcomeSourceContextV01(capture.source_canonical)

    def feedback_v01(self,capture):
        source=self.validate_capture_v01(capture)
        now=int(time.time())
        observation=feedback.build_outcome_observation_v01(source_bundle=source,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID,
            explicit_times=dict(ingested_time=now,evaluated_at=now,timestamp=now))
        value=feedback.build_outcome_feedback_v01(observation=observation,source_bundle=source,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
        return source,observation,value


class G34ControlledCurrentWorkV01:
    """Prospectively bounded simulation inputs, not an extended Sentinel session.

    Every invocation creates a current pure-only Host and current source/Root
    context. Historical permissions, monitoring expiry and observations are not
    changed. The finite wall-time window is explicit at construction.
    """
    def __init__(self, *, root, frames, reference_note, materials, valid_from, valid_to):
        c.require(type(valid_from) is int and type(valid_to) is int and 0<valid_to-valid_from<=604800,'g34_current_window')
        self.root=root;self.valid_from=valid_from;self.valid_to=valid_to
        self._inputs=c.canonical(dict(frames=frames,reference_note=reference_note,materials=materials))
        self._check_requests={}

    def evaluate_v01(self,*,store,history_key,now,invocation,additional_receipt=None):
        return self._evaluate_v01(store=store,history_key=history_key,now=now,invocation=invocation,additional_receipt=additional_receipt)

    def evaluate_check_v01(self,*,request,now,invocation):
        """The fixed evidence role executes only a previously derived task check."""
        c.require(self._check_requests.get(request['check_id'])==c.canonical(request)
            and request['root']==self.root and request['evaluated_at']==now,'g34_actual_check_request')
        return self._evaluate_v01(store=None,history_key=None,now=now,invocation=invocation,check_request=request)

    def _evaluate_v01(self,*,store,history_key,now,invocation,additional_receipt=None,check_request=None):
        from hedgehog import avf_v02 as avf, action_commit_packet_v02 as actions, work_execution_host_v01 as hosts
        from hedgehog import outcome_feedback_consumer_v01 as consumer
        from hedgehog.kernel import work_composition_v01 as work
        from . import capability_registry_v01 as caps, semantic_adapter_v01 as semantics
        c.require(type(now) is int and self.valid_from<=now<self.valid_to,'g34_current_source_expired')
        from .events_v01 import CapabilityState
        if check_request is not None:invocation='g34:check:'+check_request['check_id']
        inputs=json.loads(self._inputs);transaction='transaction:'+invocation
        diagnostic=next(row['material'] for row in inputs['materials'] if row['operation']=='sentinel.diagnostic.v01')
        c.diagnostic(diagnostic)
        records=diagnostic['checks'][0]['observations']
        check_material=dict(records=records,tick=diagnostic['checks'][0]['tick'],site=diagnostic['checks'][0]['site'],
            policy=diagnostic['contract'],purpose='local')
        if check_request is not None:
            c.require(check_request['material']==check_material,'g34_check_context_material')
            inputs['materials']=[dict(candidate_id='g34:evidence_check',operation='sentinel.observability.v01',base_score='1.0',material=check_material)]
        catalogue=(caps.admit(self.root,'sentinel.diagnostic.v01',caps.execute_diagnostic_v01),
            caps.admit(self.root,'sentinel.observability.v01',caps.execute_observability_v01))
        clock=hosts.TrustedWorkSourceSnapshotV01((),actions.build_logical_time_bridge_v01(origin_utc_epoch_seconds=now,
            seconds_per_tick=1,bridge_policy_version='g34:controlled_current'),now,'sentinel.monotonic_sample','sentinel:current',0)
        class Source:
            def __init__(self): self.reads=0
            def read_current_v01(self): self.reads+=1;return clock
        trusted=Source()
        host=hosts.build_root_work_execution_host_v01(owning_root_id=self.root,registry=actions.build_empty_action_commit_packet_registry_v02(),
            catalogue=catalogue,packet_bindings=(),current_dependency_observations=(),logical_time_bridge=clock.logical_time_bridge,trusted_source=trusted)
        source_material,_=semantics.collect(inputs['frames'],inputs['reference_note'],self.root,now)
        source,_=kernel.semantic_source('Compare bounded pure diagnostic work.',invocation,self.root,now,source_material)
        opened,discovery=store.current_v01(history_key=history_key,root=self.root,transaction=transaction,evaluation_time=now) if store else (None,dict(reason='EXPLICIT_COLD_START'))
        env=dict(pt_created_at=feedback._utc(now),kt_asof=feedback._utc(now),et_observed_at=None,ct_session_anchor=invocation,
            ttl_seconds=min(3600,self.valid_to-now),freshness_class='static',valid_from=feedback._utc(now),valid_to=feedback._utc(min(now+3600,self.valid_to)))
        bridge=opened['bridge'] if opened else abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:cold:'+c.digest(dict(transaction=transaction,now=now)),
            artifact_type='SemanticEvidence',schema_version='v1',transaction_id=transaction,owner_root_id=self.root,source_component='g34_current_history',
            authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',payload=dict(profile='G34_COLD_HISTORY_V01',prior_fp=0),trace_refs=(invocation,),parent_refs=(),time_envelope=env)
        candidates=tuple(avf.AVFCandidateV02(candidate_id=row['candidate_id'],candidate_label=row['operation'],
            base_viability_score=float(row['base_score']),ttl_valid=True) for row in inputs['materials'])
        descriptions={};keys={};checks={}
        policy_ref='policy:'+_hash(diagnostic['contract'])
        revision=hashlib.sha256(Path(semantics.__file__).read_bytes()).hexdigest()
        capability=CapabilityState().snapshot('ADVERSARIAL_SENSOR_REVIEWER')
        c.require(diagnostic['semantic_bindings'][0]['capability_snapshot']==capability,'g34_current_capability_profile')
        for row in inputs['materials']:
            is_diagnostic=row['operation']=='sentinel.diagnostic.v01'
            c.require(is_diagnostic or row['operation']=='sentinel.observability.v01','g34_fixed_current_operations')
            if not is_diagnostic: c.require(row['material']==check_material,'g34_observability_task_binding')
            route='PURE_REFERENCE_INTEGRITY' if is_diagnostic else 'PURE_OBSERVABILITY'
            subject=dict(local_root_scope_id=self.root,domain_scope_id=source.business_request_context_packet['domain'],pack_family_id='REVOCABLE_ACTION',
                advisory_source_class='CONTROLLED_DETERMINISTIC_ROLE' if is_diagnostic else 'CONTROLLED_OBSERVABILITY_CHECK',
                advisory_source_revision=revision,advice_claim_profile_id=feedback.PREDICTIVE_SOURCE_PROFILE_ID if is_diagnostic else 'G34_CURRENT_OBSERVABILITY_V01',
                route_family_id=route,task_risk_class='INFORMATIONAL',validation_profile_id='G34_TYPED_BOOLEAN_COMPLETED_WORK_V01' if is_diagnostic else 'G34_OBSERVABILITY_OUTPUT_V01',
                policy_semantics_version=policy_ref,history_key_profile_id='G3_TYPED_HISTORY_KEY_V01')
            key={k:subject[k] for k in ('local_root_scope_id','domain_scope_id','pack_family_id','route_family_id','task_risk_class','policy_semantics_version',
                'advisory_source_revision','history_key_profile_id')}
            key.update(task_class_id='REFERENCE_INTEGRITY' if is_diagnostic else 'OBSERVABILITY',capability_contract_version='capability:'+_hash(capability),
                evidence_validation_profile_id=subject['validation_profile_id'])
            description=dict(operation=row['operation'],material_sha256=c.digest(row['material']),
                definition_id=next(v.definition.definition_id for v in catalogue if v.definition.operation_id==row['operation']),
                observation_refs=sorted(v['observation_id'] for v in records),subject=subject,history_key=key)
            description['claim_id']=consumer.identity('current_claim',description)
            descriptions[row['candidate_id']]=description;keys[row['candidate_id']]=key
            check=dict(profile='G34_BOUNDED_CURRENT_ADEQUACY_V01',root=self.root,target_claim_id=description['claim_id'],
                target_subject=subject,observation_refs=description['observation_refs'],task_inputs_sha256=hashlib.sha256(self._inputs).hexdigest(),
                epoch=opened['head'] if opened else None,evaluated_at=now,policy_ref=policy_ref,operation='sentinel.observability.v01',
                definition_id=next(v.definition.definition_id for v in catalogue if v.definition.operation_id=='sentinel.observability.v01'),
                material=check_material,result_facts=c.observability(check_material))
            check['check_id']=consumer.identity('bounded_check',check)
            checks[row['candidate_id']]=check if check_request is None else None
            self._check_requests[check['check_id']]=c.canonical(check)
        contract=consumer.build_current_review_contract_v01(source_context=source,root=self.root,transaction=transaction,policy_ref=policy_ref,
            claims=descriptions,checks=checks,role='MAIN' if check_request is None else 'EVIDENCE_CHECK',check_request=check_request)
        trusted_inputs=dict(candidates=candidates,history_keys=keys,opened_history=opened,bridge=bridge,evaluated_at=now,contract=contract,source_context=source)
        projection,reports=consumer.build_current_advisory_v01(**trusted_inputs)
        review=consumer.review_current_advisory_v01(projection=projection,trusted_inputs=trusted_inputs,root=self.root,
            transaction=transaction,candidate_materials=descriptions,additional_receipt=additional_receipt)
        result=dict(projection=projection.to_plain_data(),reports=reports,review=consumer.review_to_plain_v01(review),discovery=discovery,
            context=dict(root=self.root,valid_from=self.valid_from,valid_to=self.valid_to,now=now,inputs_sha256=hashlib.sha256(self._inputs).hexdigest()),
            contract=contract.to_plain_data(),work=None)
        receipt_bridge=None
        if additional_receipt is not None and projection.to_plain_data()['trust']['review_recommended']:
            receipt_bridge=consumer.current_check_receipt_bridge_v01(check=checks[projection.to_plain_data()['selected']],
                receipt=additional_receipt,current_bridge=bridge)
            result['receipt_bridge']=abi.kernel_artifact_to_plain_dict_v01(receipt_bridge)
        runtime=dict(review=review,projection=projection,trusted_inputs=trusted_inputs,source=source,host=host,catalogue=catalogue,
            check_request=checks[projection.to_plain_data()['selected']],main_work_calls=0)
        if review[2].decision!='ACCEPT': return result,runtime
        selected=next(row for row in inputs['materials'] if row['candidate_id']==review[2].selected_candidate_id)
        material=selected['material']
        task_id='g34:check:'+check_request['check_id'] if check_request else invocation
        advisory=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:advisory:'+projection.to_plain_data()['projection_id'],
            artifact_type='SemanticEvidence',schema_version='v1',transaction_id=transaction,owner_root_id=self.root,
            source_component='g34_current_advisory',authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',
            payload=dict(advisory=projection.to_plain_data()),trace_refs=(invocation,),parent_refs=(bridge.artifact_id,),time_envelope=env)
        payload=dict(material=material,advisory_ref=projection.to_plain_data()['projection_id'],bridge_ref=bridge.artifact_id,
            root_decision_ref=review[2].decision_id,operation=selected['operation'],check_request=check_request,
            check_receipt_ref=receipt_bridge.artifact_id if receipt_bridge else None)
        proposal=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:proposal:'+c.digest(payload),
            artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id=transaction,owner_root_id=self.root,
            source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=payload,
            trace_refs=('g34:intent:'+task_id,review[2].decision_id),parent_refs=(source.bsep_packet['packet_id'],bridge.artifact_id,advisory.artifact_id)
                +((receipt_bridge.artifact_id,) if receipt_bridge else ()),time_envelope=env)
        definition=descriptions[selected['candidate_id']]['definition_id']
        item=work.WorkItemV01('consume',definition,self.root,(work.WorkInputBindingV01('material',
            work.WorkLiteralV01(caps.records(dict(material=('TEXT',c.canonical(material).decode())))[0])),),(),(),None,None)
        program,results,artifact,common=consumer.execute_reviewed_pure_work_v01(review=review,projection=projection,source_context=source,
            semantic_proposal=proposal,catalogue=catalogue,host=host,item=item,material=material,budget=work.WorkBudgetV01(1,0,0,1,0),task_id=task_id,
            trusted_inputs=trusted_inputs,additional_receipt=additional_receipt)
        output=json.loads(caps.values(results[0].result.output)['material'])
        c.require(output['input_sha256']==c.digest(material),'g34_actual_material_consumption')
        final_review=consumer.ordinary_review_v01(root=self.root,transaction=transaction,candidates={artifact.artifact_id:output},
            selected=artifact.artifact_id,scores={artifact.artifact_id:1000000},evidence_ref=artifact.artifact_id,now=now,predicate='g34_completed_pure_work')
        bsep=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=source.bsep_packet['packet_id'],artifact_type='SemanticEvidence',
            schema_version='v1',transaction_id=transaction,owner_root_id=self.root,source_component='g34_bsep_projection',authority_class='EVIDENCE_ONLY',
            lifecycle_state='VALIDATED',payload=dict(bsep=source.bsep_packet),trace_refs=(invocation,),parent_refs=(),time_envelope=env)
        work_proposal=work.work_program_candidate_to_artifact_v01(program.candidate,**common)
        artifacts=(bridge,advisory,bsep,proposal,work_proposal,program.topology_artifact,artifact)
        if receipt_bridge is not None: artifacts=artifacts+(receipt_bridge,)
        def edge(a,b,field):
            return abi.build_causal_consumption_ref_v01(producer_actor_id=a.source_component,source_artifact_id=a.artifact_id,
                output_field=field,consumer_component=b.source_component,downstream_artifact_id=b.artifact_id,
                decision_effect='CURRENT_WORK_SELECTION',disposition='USED',reason_code='used:actual_current_value',trace_refs=(invocation,))
        causal=[edge(advisory,proposal,'/advisory/selected'),edge(proposal,work_proposal,'/material'),
            edge(work_proposal,program.topology_artifact,'/work_program/items'),edge(program.topology_artifact,artifact,'/ordered_work_ids')]
        if receipt_bridge is not None:causal.append(edge(receipt_bridge,proposal,'/result_facts'))
        if opened and any(r['prior_ref'] is not None for r in projection.to_plain_data()['rows']):causal.insert(0,edge(bridge,advisory,'/prior/prior_fp'))
        if opened and projection.to_plain_data()['trust']['subject_key']==opened['trust']['subject_key']:causal.insert(0,edge(bridge,advisory,'/trust/trust_at_time_fp'))
        current_ref_count=len(causal)
        causal.extend(program.source_bindings)
        c.require(not consumer.validate_current_causal_proof_v01(projection=projection,trusted_inputs=trusted_inputs,
            artifacts=artifacts,causal_refs=tuple(causal),program=program,common=common),'g34_actual_causal_bundle')
        result['work']=dict(operation=selected['operation'],proposal=abi.kernel_artifact_to_plain_dict_v01(proposal),
            program=plain(program),results=plain(results),artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),output=output,
            final_review=consumer.review_to_plain_v01(final_review),causal=plain(tuple(causal)),
            causal_artifacts=[abi.kernel_artifact_to_plain_dict_v01(v) for v in artifacts],causal_validation='PASS',
            causal_inventory=dict(current_refs=current_ref_count,native_refs=len(program.source_bindings),combined_refs=len(causal),deduplicated=0),
            source=dict(bsep=source.bsep_packet,business=source.business_request_context_packet,
                evaluation_time=source.g2a_evaluation_time,evaluation_context=source.g2a_evaluation_context_id),trusted_source_reads=trusted.reads)
        runtime.update(program=program,results=results,common=common,artifact=artifact,advisory=advisory,causal=tuple(causal),artifacts=artifacts,
            item=item,material=material,proposal=proposal,additional_receipt=additional_receipt,main_work_calls=int(check_request is None))
        return result,runtime
