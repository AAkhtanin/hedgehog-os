"""Finite coordinator: deterministic work, one local Root/Host, mock targets."""
from dataclasses import replace
import json
from pathlib import Path
import secrets
import threading
import time
from hedgehog import action_commit_packet_v02 as a, work_execution_host_v01 as hosts
from hedgehog.kernel import work_composition_v01 as w, abi_v01 as abi
from . import contracts_v01 as c, capability_registry_v01 as caps, kernel_adapter_v01 as k
from . import semantic_adapter_v01 as semantics
from .evidence_v01 import phase, plain, save


class Sentinel:
    def __init__(self, directory, fixture, *, harness=None):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=False)
        (self.directory/'logs').mkdir()
        self.id='sentinel:'+''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(12))
        self.root='SiteSafetyRoot:'+self.id
        self.fixture=json.loads(c.canonical(fixture));self.frames=[c.measurement(v) for v in fixture['frames']]
        self.source=k.CurrentSource();self.expires=self.source.epoch+7200;self.version=0
        self.contract=dict(c.POLICY);self.executed={};self.timings=[];self.history=[]
        self.signal=False;self.cadence_seconds=c.POLICY['normal_cadence_seconds'];self.tick=0;self.next_intake=0;self.intakes=[]
        self.source_hashes=c.digest(fixture);self.resource_plan={'configuration':self.id,'signal':self.id}
        self.catalogue=caps.catalogue(self.root,self.id)
        self.host=hosts.build_root_work_execution_host_v01(owning_root_id=self.root,registry=a.build_empty_action_commit_packet_registry_v02(),
            catalogue=self.catalogue,packet_bindings=(),current_dependency_observations=(),logical_time_bridge=self.source.snapshot.logical_time_bridge,
            trusted_source=self.source)
        self.request='Inspect local slope measurements and propose a finite diagnostic.'
        material,semantic=semantics.collect(self.frames,fixture['reference_note'],self.root,self.source.sample().evaluation_time,harness=harness)
        self.semantic_responses=[material];self.semantic_evidence=semantic
        source,_=k.semantic_source(self.request,self.id,self.root,self.source.sample().evaluation_time,material)
        self.program,self.results,self.work_artifact=k.materialize(self,material,source)
        output=json.loads(caps.values(self.results[-1].result.output)['material'])
        self.diagnostic_review=k.root_review(self.root,'transaction:'+self.id,c.identity('diagnostic_review',output),self.id,
            dict(actual_work_completed=all(v.status=='COMPLETED' for v in self.results),healthy=output['healthy'],
                 selected_actual=output['selection']==material['selection']),self.work_artifact.artifact_id,
            self.program.candidate.bsep_ref,self.program.topology_artifact.artifact_id,self.source.sample().evaluation_time,claim_value=output)
        save(self.directory/'semantic_work.json',dict(semantic=semantic,program=self.program.candidate,results=self.results,
            work_artifact=abi.kernel_artifact_to_plain_dict_v01(self.work_artifact),consumed_review=self.diagnostic_review[2]))
        self.journal('SENTINEL_READY',root=self.root,profile=semantic['profile'],effects=len(self.executed))

    def journal(self,name,**values):return phase(self.directory,name,**values)

    def rain_dependency(self):
        return dict(rainfall=next(dict(v) for v in self.frames if v['sensor']=='rainfall'))

    def stable_sources(self):
        return dict(local=[dict(v) for v in self.frames if v['sensor']!='rainfall'],site=self.fixture['site'],policy=self.contract,
                    health=dict(collector='HEALTHY',configuration_target='MOCK_AVAILABLE'))

    def authorization_fact(self, value):
        return dict(command=value,rainfall=self.rain_dependency(),stable_sources=self.stable_sources())

    def validate_effect(self, inputs):
        c.require(inputs['session']==self.id and inputs['version']==self.version, 'current_local_invocation')
        command=json.loads(inputs['command']);op=command.get('op')
        c.require(self.source.snapshot.evaluation_time < self.expires, 'monitoring_expired')
        if op=='APPLY_MONITORING_CONFIG':
            c.require(set(command)=={'op','cadence_seconds','basis_ref'} and command['cadence_seconds'] in (15,60)
                and bool(command['basis_ref']), 'configuration_closed_inputs')
        elif op=='SET_LOCAL_SIGNAL_STATE':
            c.require(set(command)=={'op','state','basis_ref'} and command['state'] in ('ON','OFF') and bool(command['basis_ref']), 'signal_closed_inputs')
        else:raise ValueError('operation_not_admitted')

    def execute_effect(self, inputs, invocation_id):
        # This target only applies bounded inputs; Root/currentness remain outside it.
        command=json.loads(inputs['command'])
        if command['op']=='APPLY_MONITORING_CONFIG':
            self.cadence_seconds=command['cadence_seconds'];self.next_intake=self.tick+self.cadence_seconds
        else:self.signal=command['state']=='ON'
        result=dict(op=command['op'],cadence_seconds=self.cadence_seconds,next_intake=self.next_intake,signal=self.signal,
                    invocation_id=invocation_id,adapter_kind='DETERMINISTIC_MOCK')
        self.executed[invocation_id]=result
        return result

    def intake(self,tick):
        c.require(type(tick) is int and tick>=self.tick,'scenario_clock_rollback')
        self.tick=tick
        if tick<self.next_intake:return None
        c.require(all(v['scenario_tick']<=tick for v in self.frames),'future_reading_at_intake')
        sample=dict(scenario_tick=tick,frames=json.loads(c.canonical(self.frames)),cadence_seconds=self.cadence_seconds,
                    current_wall=self.source.sample().evaluation_time)
        self.intakes.append(sample);self.next_intake=tick+self.cadence_seconds
        self.journal('ACTUAL_LOCAL_INTAKE',scenario_tick=tick,cadence_seconds=self.cadence_seconds)
        return sample

    def prepare_config(self, *, reviewed=False):
        current,_=semantics.collect(self.frames,self.fixture['reference_note'],self.root,
            self.source.sample().evaluation_time,policy=self.contract)
        if reviewed:
            material=dict(current,stable_sources=json.loads(c.canonical(self.stable_sources())))
            self.monitor_review=k.assemble(self,material)
        ref=self.monitor_review['results'][0].result.result_id if reviewed else self.results[-1].result.result_id
        material=dict(kind='CURRENT_CONFIGURATION',rainfall=self.rain_dependency()['rainfall'],contract=dict(self.contract),diagnostic_result_ref=ref)
        work=self.pure_consumer('sentinel.configuration.v01',material)
        output=json.loads(caps.values(work[1][0].result.output)['material'])
        c.require(output['input_sha256']==c.digest(material) and output['contract']==self.contract,'configuration_current_work')
        self.configuration_work=work
        basis=k.review_work(self,work,material)
        save(self.directory/'configuration_work.json',dict(material=material,program=work[0].candidate,results=work[1],output=output,
            artifact=abi.kernel_artifact_to_plain_dict_v01(work[2])))
        value=dict(op='APPLY_MONITORING_CONFIG',cadence_seconds=output['cadence_seconds'],basis_ref=work[2].artifact_id)
        authorization,inputs,observation,review=k.prepare_command(self,value,dict(actual_diagnostic=self.results[-1].status=='COMPLETED',
            actual_current_rainfall=c.measurement(self.rain_dependency()['rainfall'])['healthy']),accepted_work=basis)
        clock=self.source.sample(observation)
        packet,_=hosts.install_current_action_v01(self.host,**authorization,inputs=inputs,admission_id=self.catalogue[2].admission_id,
            expected_revision=self.host.revision,**clock_args(clock))
        self.monitor_pending=dict(authorization=authorization,inputs=inputs,observation=observation,review=review,packet_id=packet,
                                 fact=self.last_prepared_fact,registry=self.host.registry)
        self.initial_capture=hosts.capture_current_action_source_v01(self.host,packet_id=packet,expected_revision=self.host.revision,**clock_args(self.source.sample()))
        if reviewed:self.monitor_baseline=k.prepare_delta_baseline(self)
        save(self.directory/'pending.json',dict(packet_id=packet,inputs=inputs,review=review[2],observation=observation,
            expires=authorization['root_bound'].canonical_projection.temporal_authority.expires_at_utc,current=self.initial_capture.evaluation_time,
            effects=len(self.executed),capture_ordinal=self.initial_capture.capture_ordinal,source_revision=self.initial_capture.source_revision))
        return packet

    def dispatch_pending(self):
        clock=self.source.sample();token=caps.EXECUTION.set(self)
        try:
            registry,_=hosts.dispatch_current_action_v01(self.host,packet_id=self.monitor_pending['packet_id'],task_id=self.id,
                expected_revision=self.host.revision,**clock_args(clock))
        finally:caps.EXECUTION.reset(token)
        receipt=registry.action_packet_fulfillment_attempt_contexts[-1].receipt
        c.require(receipt is not None,'actual_native_receipt')
        save(self.directory/'pending_receipt.json',abi.kernel_artifact_to_plain_dict_v01(receipt))
        return receipt

    def rainfall_delta(self):
        c.require(self.monitor_review['material']['stable_sources']==self.stable_sources(),'policy_change_requires_fresh_baseline')
        pending=self.monitor_pending;prior=pending['observation'];before_stable=c.canonical(self.stable_sources())
        self.ingest_rainfall(self.fixture['changed_rainfall'])
        self.changed_dependency=self.rain_dependency()
        c.require(c.canonical(self.stable_sources())==before_stable,'only_rainfall_changed')
        fact=dict(pending['fact'],rainfall=self.changed_dependency);sha=c.digest(fact);clock=self.source.sample()
        start,end=clock.evaluation_time,min(clock.evaluation_time+3600,self.expires)
        envelope=a.build_action_dependency_time_envelope_id_v01(dependency_id=prior.dependency_id,evidence_ref=prior.evidence_ref,
            content_sha256=sha,freshness_policy_id=prior.freshness_policy_id,source_provenance_refs=prior.source_provenance_refs,
            valid_from_utc=start,valid_to_utc=end)
        observation=a.build_action_dependency_current_observation_v01(dependency_id=prior.dependency_id,evidence_ref=prior.evidence_ref,
            observed_content_sha256=sha,time_envelope_id=envelope,freshness_policy_id=prior.freshness_policy_id,
            source_provenance_refs=prior.source_provenance_refs,valid_from_utc=start,valid_to_utc=end,observed_at_utc=start,
            observation_context_id=clock.evaluation_context_id)
        clock=self.source.sample(observation)
        capture=hosts.capture_current_action_source_v01(self.host,packet_id=pending['packet_id'],expected_revision=self.host.revision,**clock_args(clock))
        invalidation=a.build_action_invalidation_evidence_v01(source_invalidation_event_ref=c.identity('rainfall_change',fact),
            packet_id=pending['packet_id'],dependency_id=prior.dependency_id,invalidation_class='DEPENDENCY_CHANGED',
            evidence_ref=prior.evidence_ref,evidence_sha256=sha,observed_status='CHANGED',time_envelope_id=prior.time_envelope_id,
            freshness_policy_id=prior.freshness_policy_id,owning_local_root_id=self.root,accepted_by_local_root_id=self.root,
            authority_effect='DETERMINISTIC_BLOCK',**clock_args(capture))
        effects=len(self.executed);expiry=pending['authorization']['root_bound'].canonical_projection.temporal_authority.expires_at_utc
        c.require(clock.evaluation_time<expiry, 'old_pending_must_be_live')
        try:self.dispatch_pending()
        except ValueError as error:c.require(str(error)=='host_current_action_not_executable','wrong_stale_refusal:'+str(error))
        else:raise ValueError('stale_packet_executed')
        c.require(len(self.executed)==effects and not self.signal,'stale_refusal_no_effect')
        capture=hosts.capture_current_action_source_v01(self.host,packet_id=pending['packet_id'],expected_revision=self.host.revision,**clock_args(self.source.sample()))
        self.current_capture=capture
        save(self.directory/'invalidation.json',dict(invalidation=invalidation,observation=observation,current=capture.evaluation_time,
            old_expiry=expiry,effect_delta=0,stable_sha256=c.digest(self.stable_sources())))
        self.delta=k.recompute(self,capture,invalidation,start)
        typed=self.pure_consumer('sentinel.configuration.v01',self.delta['consumed'])
        basis=k.review_work(self,typed,self.delta['consumed'])
        output=json.loads(caps.values(typed[1][0].result.output)['material'])
        value=dict(op='APPLY_MONITORING_CONFIG',cadence_seconds=output['cadence_seconds'],basis_ref=typed[2].artifact_id)
        token=caps.EXECUTION.set(self)
        try:
            effect=k.dispatch(self,value,dict(actual_E=self.delta['report'].status=='PASS',actual_result_consumed=
                output['recomputed_result_ref']==self.delta['consumed']['recomputed_result_ref'],preserved_sources=c.canonical(self.stable_sources())==before_stable),accepted_work=basis)
        finally:caps.EXECUTION.reset(token)
        save(self.directory/'new_configuration.json',dict(effect=effect,typed_results=typed[1],consumed=self.delta['consumed']))
        c.require(not self.signal and self.intake(self.next_intake-1) is None,'no_signal_or_early_intake')
        intake=self.intake(self.next_intake)
        c.require(intake['cadence_seconds']==output['cadence_seconds'],'actual_new_cadence')
        return effect

    def ingest_rainfall(self,value):
        value=c.measurement(value)
        c.require(value['scenario_tick']>=self.tick,'rainfall_arrival_clock_rollback')
        self.tick=value['scenario_tick']
        self.frames=[dict(value) if v['sensor']=='rainfall' else v for v in self.frames]
        self.journal('RAINFALL_INGESTED',scenario_tick=self.tick,observed_at=value['scenario_tick'])

    def pure_consumer(self,operation,material,*,semantic_source_override=None):
        now=self.source.sample().evaluation_time
        if 'semantic_bindings' in material:
            semantics.validate_current(material,self)
            source_material=material
        else:
            source_material,_=semantics.collect(self.frames,self.fixture['reference_note'],self.root,now,policy=self.contract)
        source,_=k.semantic_source(self.request,self.id,self.root,now,source_material)
        if semantic_source_override is not None:
            c.require(source.bsep_packet==semantic_source_override.bsep_packet,'stale_bootstrap_bsep')
            source=semantic_source_override
        proposal_material=material
        if hasattr(self,'book'):
            self.work_request_sequence=getattr(self,'work_request_sequence',0)+1
            proposal_material=dict(material=material,current_event=self.tick,capability_revision=self.capabilities.revision,
                observation_ids={key:value['observation_id'] for key,value in self.book.latest.items()},
                invocation_ordinal=self.work_request_sequence)
        proposal=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('consumer',proposal_material),artifact_type='SemanticArchitectProposal',
            schema_version='v1',transaction_id='transaction:'+self.id,owner_root_id=self.root,source_component='semantic_architect',
            authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=proposal_material,trace_refs=('intent:'+self.id,),
            parent_refs=(source.bsep_packet['packet_id'],),time_envelope=dict(pt_created_at=k.stamp(now),kt_asof=k.stamp(now),et_observed_at=None,
                ct_session_anchor=self.id,ttl_seconds=3600,freshness_class='static',valid_from=k.stamp(now),valid_to=k.stamp(now+3600)))
        admitted=next(v for v in self.catalogue if v.definition.operation_id==operation)
        item=w.WorkItemV01('consume',admitted.definition.definition_id,self.root,(w.WorkInputBindingV01('material',
            w.WorkLiteralV01(caps.records(dict(material=('TEXT',c.canonical(material).decode())))[0])),),(),(),None,None)
        common=dict(catalogue=self.catalogue,source_context=source,semantic_proposal=proposal)
        candidate=w.build_work_program_candidate_v01(task_id=self.id,previous_revision_id=None,intent_ref='intent:'+self.id,
            bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,
            budget=w.WorkBudgetV01(getattr(self,'work_limit',1),0,0,getattr(self,'work_limit',1),0),items=(item,),trigger_evidence_refs=(),**common)
        if hasattr(self,'routes'):
            info=k.information(self,dict(contract=self.contract,operation=operation,material_ref=c.identity('routed_material',material)),now)
            _,common=k.source_family(self,common,item,candidate,now,info,selected_mode=getattr(self,'work_mode','deterministic'))
        program=w.materialize_work_program_v01(candidate,**common)
        results=w.advance_work_program_v01(program,host_map={self.root:self.host},**common)
        c.require(len(results)==1 and results[0].status=='COMPLETED','actual_typed_consumer')
        artifact=w.work_program_result_to_artifact_v01(program,results,host_map={self.root:self.host},**common)
        self.last_work_common=(program,common)
        return program,results,artifact

    def critical_while_pending(self):
        old=c.canonical(dict(frames=self.frames,context='optional_site_cloud_context',root=self.root))
        started=threading.Event();release=threading.Event();returned=[]
        worker=threading.Thread(target=pending_stub,args=(old,self.directory,started,release,returned),name='sentinel-optional-provider-stub')
        worker.start();c.require(started.wait(5),'pending_stub_start')
        try:
            self.frames=[dict(self.fixture['critical_local'][0]),dict(self.fixture['critical_local'][1]),self.rain_dependency()['rainfall']]
            self.tick=90;observation=self.journal('INDEPENDENT_CRITICAL_OBSERVATION',frames=self.frames)
            hard=c.critical(self.frames,self.tick,self.contract);c.require(hard,'hard_critical_evidence_missing')
            ref=c.identity('hard_critical',dict(frames=self.frames,tick=self.tick))
            token=caps.EXECUTION.set(self)
            try:effect=k.dispatch(self,dict(op='SET_LOCAL_SIGNAL_STATE',state='ON',basis_ref=ref),dict(independent_local_hard_floor=hard,optional_response_pending=not returned))
            finally:caps.EXECUTION.reset(token)
            completed=self.journal('CRITICAL_EFFECT_COMPLETED',signal=self.signal,packet_id=effect['packet_id'])
            c.require(self.signal and not returned,'signal_before_optional_response')
            count=len(self.executed)
            try:hosts.dispatch_current_action_v01(self.host,packet_id=effect['packet_id'],task_id=self.id,
                expected_revision=self.host.revision,**clock_args(self.source.sample()))
            except ValueError as error:duplicate=str(error)
            else:raise ValueError('duplicate_signal_executed')
            c.require(len(self.executed)==count,'duplicate_no_effect')
        finally:
            release.set();worker.join(10)
            c.require(not worker.is_alive(),'owned_stub_not_reaped')
        c.require(returned and completed['monotonic']<returned[0]['monotonic'],'critical_event_order')
        save(self.directory/'critical_pending.json',dict(old_context_sha256=c.digest(old),observation=observation,
            effect=effect,completed=completed,late_response=returned[0],duplicate_refusal=duplicate,final_signal=self.signal,
            implicit_off=False,worker_joined=True,provider_mode='CONTROLLED_BARRIER_STUB',actual_provider_calls=0))
        return effect


def clock_args(value):
    return dict(evaluation_time=value.evaluation_time,evaluation_time_source=value.evaluation_time_source,evaluation_context_id=value.evaluation_context_id)


def pending_stub(immutable_context, directory, started, release, returned):
    phase(directory,'OPTIONAL_PROVIDER_REQUEST_STARTED',context_sha256=c.digest(immutable_context),mode='CONTROLLED_BARRIER_STUB')
    started.set();release.wait()
    row=phase(directory,'OPTIONAL_PROVIDER_RESPONSE_RETURNED',context_sha256=c.digest(immutable_context),
        status='HISTORICAL_ONLY_NOT_CURRENT',semantic_answer='Request belongs to the old context.')
    returned.append(row)

"""Local DRS semantic candidates, current Root descent and no retained permissions."""
from dataclasses import asdict
from datetime import datetime,timezone
import json
from pathlib import Path
from hedgehog.drs import LocalDRS
from hedgehog import local_drs_resolver as resolver
from hedgehog import drs_semantic_address_v01 as address, drs_memory_resolution_v01 as memory
from hedgehog.kernel import integrity_replay_v01 as integrity
from . import contracts_v01 as c, kernel_adapter_v01 as kernel

MEMORY_POLICY='sentinel.semantic_recipe.v01'
DOMAIN='LANDSLIDE_SENTINEL'


def stamp(now):
    return datetime.fromtimestamp(now,timezone.utc).isoformat()


def memory_dependencies(session):
    return dict(calibration=session.contract['calibration'],site=session.fixture['site'],policy=MEMORY_POLICY,
        monitoring_policy=c.digest(session.contract),health={ch:any(v['sensor']==ch and v['healthy'] for v in session.frames)
            for ch in ('displacement','reserve')})


def _review(root,material,now,predicate='sentinel_semantic_memory_writeback'):
    ref=c.identity('memory_material',material)
    return kernel.root_review(root,'transaction:'+ref,ref,'sentinel:semantic_memory',
        dict(finite_content=len(c.canonical(material))<16384,no_effect_grant=True),ref,'sentinel:memory:bsep','sentinel:memory:topology',now,
        predicate=predicate,claim_value=material)


def _record(material,review,now,ttl,root):
    addr=address.build_semantic_address_v01(namespace='sentinel',domain=DOMAIN,subject_class=material['kind'],
        intent_class='context_lookup',meaning_schema_id='sentinel.semantic_recipe',meaning_schema_version='v0.1')
    env=address.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=now,ct_context_anchor=now,
        ttl_seconds=ttl,valid_from=now,valid_to=now+ttl,source_observed_at=now,source_reported_at=now,
        system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:sentinel:recipe')
    auth=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=root,
        source_root_decision_input_id=review[1].decision_input_id,source_root_decision_id=review[2].decision_id,
        source_root_decision_hash=c.digest(kernel.roots.root_decision_result_to_plain_dict_v01(review[2])),
        authority_scope_fingerprint=c.digest(material['dependencies']),root_acceptance_state='ACCEPTED_WORK',recording_component='sentinel:memory')
    summary_value=material['value']
    summary=c.canonical(summary_value).decode()
    c.require(len(summary)<=1024,'semantic_memory_summary_bound')
    return address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
        safe_summary=summary,semantic_tags=('monitoring',),resonance_reason='Bounded semantic content, fresh review required.',
        memory_pointers=(),artifact_pointers=(),source_reference_ids=tuple(
            c.digest(ref.encode()) if material['kind']=='semantic_recipe' else ref for ref in material['sources']),lineage_edges=(),time_envelope=env,
        authority_envelope=auth,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),reuse_policy_class='CONTEXT_ONLY',
        policy_version=MEMORY_POLICY,schema_versions=(MEMORY_POLICY,),content_fingerprint=c.digest(material),recording_component='sentinel:memory')


class SentinelMemory:
    def __init__(self,directory):
        self.drs=LocalDRS(Path(directory))
        self.events=[]

    def _write(self,session,kind,value,sources,ttl):
        c.require(type(ttl) is int and 0<ttl<=86400,'memory_finite_validity')
        c.require(session.source.sample().evaluation_time < session.expires, 'memory_current_time')
        now=session.source.sample().evaluation_time
        material=dict(kind=kind,request=session.request,dependencies=memory_dependencies(session),value=value,sources=sources)
        review=_review(session.root,material,now)
        record=_record(material,review,now,ttl,session.root)
        plain=address.meaning_record_to_plain_data_v01(record)
        result=resolver.write_semantic_record(self.drs,resolver.SemanticDRSRecordInput(record_id=record.meaning_record_id,
            domain=DOMAIN,content=dict(kind=kind,request=session.request,worldstate=memory_dependencies(session),material=material,
                record=plain,root_result=kernel.roots.root_decision_result_to_plain_dict_v01(review[2])),
            semantic_keys=('monitoring',kind),time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=stamp(now),
                ct_session_anchor=session.id,ttl_seconds=ttl,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+ttl)),
            provenance=dict(request_id=session.id,created_by='root_orchestrator',trace_refs=[dict(trace_id=sources[0])]),
            root_final_ref=review[2].decision_id,worldstate_ref=c.digest(material['dependencies'])))
        self.events.append(dict(op='WRITE',record=result,root_input=kernel.roots.root_decision_input_to_plain_dict_v01(review[1]),
            records_written=1,storage='EXPLICIT_DURABLE_LOCAL_DRS',creates_permission=False))
        return record.meaning_record_id

    def remember(self,session,ttl=3600):
        c.require(all(r.status=='COMPLETED' for r in session.results),'memory_actual_diagnostic_work')
        actual=json.loads(caps.values(session.results[-1].result.output)['material'])
        # Opaque result identities belong to source references, not free-text summaries.
        value=dict(selection=actual['selection'],checked_sensors=actual['checked_sensors'],healthy=actual['healthy'])
        return self._write(session,'semantic_recipe',value,
            [session.work_artifact.artifact_id,session.results[-1].result.result_id],ttl)

    def select(self,*,root,request,dependency,now,kind='semantic_recipe',policy=MEMORY_POLICY):
        query=resolver.SemanticResolveQuery(query_id=c.identity('memory_search',dict(root=root,request=request,dependency=dependency,now=now,kind=kind)),
            domain=DOMAIN,semantic_terms=('monitoring',kind),content_filters=dict(kind=kind,request=request),
            temporal_query=dict(as_of=stamp(now)),worldstate=dependency,require_root_review=True)
        report=resolver.resolve_semantic_candidates(self.drs,query,layers=('work',))
        event=dict(op='SEARCH',query=asdict(query),report=asdict(report),evaluations=[])
        self.events.append(event)
        for candidate in report.candidates:
            wrapper=self.drs.read_record('work',candidate.record_id)
            value=wrapper['content'];material=value['material'];plain=value['record']
            oldtime=plain['time_envelope'];owner=plain['authority_envelope']['owning_local_root_id']
            # Rebuild historical value only; this is not current execution authority.
            historical=_review(owner,material,oldtime['pt_created_at'])
            c.require(kernel.roots.root_decision_result_to_plain_dict_v01(historical[2])==value['root_result'],'memory_historical_root_binding')
            record=_record(material,historical,oldtime['pt_created_at'],oldtime['ttl_seconds'],owner)
            c.require(address.meaning_record_to_plain_data_v01(record)==plain and record.meaning_record_id==candidate.record_id,'memory_record_content_binding')
            current=memory.build_drs_temporal_query_v01(query_mode='CURRENT_DECISION',semantic_address_id=record.semantic_address.semantic_address_id,
                scope_fingerprint=c.digest(dependency),as_of=now,evaluation_time=now,evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',
                time_range_start=now,time_range_end=now+1,required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),
                freshness_policy_id=record.time_envelope.freshness_policy_id,max_age_seconds=record.time_envelope.ttl_seconds,
                domain=DOMAIN,risk_class='LOW',reuse_intent='CONTEXT',requested_reuse_classes=('CONTEXT_ONLY',),
                required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN','TIME_FITNESS','POLICY_COMPATIBILITY',
                    'SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),forbidden_changes=('POLICY_CHANGED',),
                policy_version=policy,schema_versions=(MEMORY_POLICY,),owning_local_root_id=root)
            ev=memory.evaluate_drs_candidate_v01(semantic_address=record.semantic_address,query=current,meaning_record=record)
            event['evaluations'].append(memory.query_evaluation_state_to_plain_data_v01(ev))
            if candidate.blocked or not ev.eligible_for_ranking:continue
            budget=memory.build_memory_descent_budget_v01(max_depth=0,max_records_opened=1,max_pointers_opened=0,max_artifacts_opened=0,
                max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
            plan=memory.build_retrieval_plan_v01(query_id=current.query_id,semantic_address_id=record.semantic_address.semantic_address_id,
                proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),
                requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(),reason_codes=())
            review=kernel.root_review(root,current.query_id,plan.retrieval_plan_id,record.semantic_address.semantic_address_id,
                dict(eligible=ev.eligible_for_ranking,current_dependency=material['dependencies']==dependency),record.meaning_record_id,
                'sentinel:memory:bsep','sentinel:memory:topology',now,predicate='approve_controlled_memory_descent_plan_v01',
                claim_value=memory.retrieval_plan_to_plain_data_v01(plan))
            root_hash=integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
                payload=c.canonical(kernel.roots.root_decision_result_to_plain_dict_v01(review[2])))
            req=memory.build_memory_descent_request_v01(retrieval_plan_id=plan.retrieval_plan_id,query_id=current.query_id,
                owning_local_root_id=root,root_kernel_id=review[0].kernel_id,root_decision_input_id=review[1].decision_input_id,
                root_decision_id=review[2].decision_id,root_decision_hash=root_hash,requested_descent_class='SUMMARY_ONLY',approved_descent_class='SUMMARY_ONLY',
                proposed_budget_id=budget.memory_descent_budget_id,approved_budget=budget,approved_record_ids=(record.meaning_record_id,),
                approved_memory_pointer_ids=(),approved_artifact_pointer_ids=())
            result=memory.execute_local_memory_descent_v01(retrieval_plan=plan,proposed_budget=budget,descent_request=req,
                root_kernel=review[0],root_decision_input=review[1],root_decision_result=review[2],source_records=(record,))
            c.require(result.limits_respected and not result.reason_codes and result.opened_record_ids==(record.meaning_record_id,), 'memory_descent_refused')
            event.update(query_current=memory.drs_temporal_query_to_plain_data_v01(current),plan=memory.retrieval_plan_to_plain_data_v01(plan),
                descent=memory.memory_descent_result_to_plain_data_v01(result),root=kernel.roots.root_decision_result_to_plain_dict_v01(review[2]))
            selected=json.loads(result.safe_summaries[0])
            return selected,dict(record_id=record.meaning_record_id,descent_id=result.memory_descent_result_id)
        return None


class ControlledEpisode(Sentinel):
    """One continuing coordinator; story labels never select its decisions."""
    def __init__(self,directory,fixture):
        from .events_v01 import EventBook,AllocationLedger,CapabilityState
        from .incident_policy_v01 import Incident
        from .outbox_v01 import Outbox,Receiver
        super().__init__(directory,fixture)
        self.book=EventBook();self.budgets=AllocationLedger();self.capabilities=CapabilityState()
        self.budgets.allocate('pure_work',32,'continuing_episode_local_compute')
        self.incident=Incident();self.routes=[];self.work_mode='deterministic';self.role_results=[]
        self.outbox=Outbox(self.directory/'outbox');self.receiver=Receiver(self.directory/'receiver')
        self.pending_worker=None;self.pending_return=[];self.effects=[];self.report=None
        save(self.directory/'signal_readback.json',dict(signal=False,receipt_ref=None))

    def ingest(self,records,tick):
        self.book.ingest(records,tick);self.tick=self.book.tick
        from .events_v01 import compatibility
        self.frames=[compatibility(record) for record in self.book.latest.values() if record['value'] is not None
            and record['channel'] in ('rainfall','displacement','reserve')]
        self.journal('EVENTS_INGESTED',tick=tick,records=records)

    def ingest_rainfall(self,value):
        from .events_v01 import observation
        old=self.book.latest['rainfall']
        self.ingest([observation('rainfall',value['value'],value['scenario_tick'],old['sequence']+1)],value['scenario_tick'])
        c.require(all(self.book.current(ch,'configuration') for ch in ('displacement','reserve')),'retained_configuration_current')

    def intake(self,tick):
        self.book.advance(tick)
        result=super().intake(tick)
        if result is not None:
            from .events_v01 import compatibility
            result['frames']=[compatibility(v) for v in self.book.latest.values() if v['value'] is not None]
            result['absent_channels']=[ch for ch,v in self.book.latest.items() if v['value'] is None]
            result['observation_ids']={ch:v['observation_id'] for ch,v in self.book.latest.items()}
            result['observed_at']={ch:v['observed_end'] for ch,v in self.book.latest.items()}
            c.require(all(t<=tick for t in result['observed_at'].values()),'future_rich_intake')
        return result

    def command(self,value,checks,*,accepted_work=None):
        token=caps.EXECUTION.set(self)
        try:effect=k.dispatch(self,value,checks,accepted_work=accepted_work)
        finally:caps.EXECUTION.reset(token)
        self.effects.append(effect);return effect

    def validate_effect(self,inputs):
        command=json.loads(inputs['command']);op=command.get('op')
        if op=='READ_RESERVE_SERIES':
            c.require(inputs['session']==self.id and inputs['version']==self.version,'current_local_invocation')
            c.require(set(command)=={'op','basis_ref','source_ref','tick'} and command['tick']==self.tick,'series_read_current')
            c.require(command['source_ref']=='synthetic:reserve_series:v01' and bool(command['basis_ref']),'series_read_source')
            c.require(self.source.snapshot.evaluation_time<self.expires,'monitoring_expired')
            basis=getattr(self,'accepted_plans',{}).get(command['basis_ref'])
            output=k.validate_reviewed_work(self,basis)
            c.require(output['stage']=='PLAN' and any(v['action']==op and v['source_ref']==command['source_ref']
                for v in output['checks']),'series_current_selected_plan')
        elif op in ('QUEUE_INCIDENT_REPORT','DELIVER_INCIDENT_REPORT'):
            c.require(inputs['session']==self.id and inputs['version']==self.version,'current_local_invocation')
            c.require(self.source.snapshot.evaluation_time<self.expires,'monitoring_expired')
            expected={'op','basis_ref','report'} if op=='QUEUE_INCIDENT_REPORT' else {'op','basis_ref','message_id'}
            c.require(set(command)==expected and bool(command['basis_ref']),'report_command_shape')
            if op=='DELIVER_INCIDENT_REPORT':
                c.require(self.capabilities.available('site_upload'),'upload_unavailable')
                self.outbox.read(command['message_id'])
            else:c.require(len(c.canonical(command['report']))<8192 and command['report']['classification']=='TEST','report_bound')
        else:super().validate_effect(inputs)

    def execute_effect(self,inputs,invocation_id):
        command=json.loads(inputs['command']);op=command['op']
        if op=='READ_RESERVE_SERIES':
            result=dict(op=op,classification='MOCK_SOURCE_READ',records=self.read_reserve_series(command['source_ref'],command['tick']),
                invocation_id=invocation_id,adapter_kind='DETERMINISTIC_MOCK')
            self.executed[invocation_id]=result;return result
        if op in ('QUEUE_INCIDENT_REPORT','DELIVER_INCIDENT_REPORT'):
            result=(self.outbox.queue(command['report']) if op=='QUEUE_INCIDENT_REPORT' else
                    self.outbox.deliver(command['message_id'],self.receiver))
            result=dict(result,op=op,invocation_id=invocation_id,adapter_kind='DETERMINISTIC_MOCK')
            self.executed[invocation_id]=result;return result
        result=super().execute_effect(inputs,invocation_id)
        if op=='SET_LOCAL_SIGNAL_STATE':save(self.directory/'signal_readback.json',dict(signal=self.signal,receipt_ref=invocation_id))
        if op=='APPLY_MONITORING_CONFIG':result.update(configured_at=self.tick,due_at=self.next_intake)
        return result

    def read_signal(self):
        return json.loads((self.directory/'signal_readback.json').read_bytes())

    def local_work(self):
        from .incident_policy_v01 import features
        current=features(self.book,contract=self.contract)
        material=dict(selection='REFERENCE_INTEGRITY',frames=json.loads(c.canonical(self.frames)),contract=self.contract)
        work=self.pure_consumer('sentinel.diagnostic.v01',material)
        output=json.loads(caps.values(work[1][0].result.output)['material'])
        review=k.root_review(self.root,'transaction:'+self.id,c.identity('local_features',dict(current=current,output=output)),self.id,
            dict(actual_work=work[1][0].status=='COMPLETED',current_sources=bool(current['source_ids'])),work[2].artifact_id,
            work[0].candidate.bsep_ref,work[0].topology_artifact.artifact_id,self.source.sample().evaluation_time,claim_value=current)
        return dict(features=current,result=plain(work[1]),root=plain(review[2]))

    def observation_work(self,purpose='local'):
        material=dict(records=list(self.book.latest.values()),tick=self.tick,site=self.fixture['site'],policy=self.contract,purpose=purpose)
        work=self.pure_consumer('sentinel.observability.v01',material)
        result=json.loads(caps.values(work[1][0].result.output)['material'])
        review=k.root_review(self.root,'transaction:'+self.id,c.identity('observation_work',result),self.id,
            dict(actual_work=work[1][0].status=='COMPLETED',input_consumed=result['input_sha256']==c.digest(material)),
            work[2].artifact_id,work[0].candidate.bsep_ref,work[0].topology_artifact.artifact_id,self.source.sample().evaluation_time,claim_value=result)
        return dict(material=material,result=result,program=plain(work[0].candidate),work=plain(work[1]),root=plain(review[2]))

    def update_policy(self,policy):
        c.validate_policy(policy)
        old=c.digest(self.contract);self.contract=json.loads(c.canonical(policy));self.version+=1
        self.journal('POLICY_REVISION',old_sha256=old,current=self.contract,version=self.version)
        if hasattr(self,'monitor_pending'):
            prior=self.monitor_pending['observation'];clock=self.source.sample()
            digest=c.digest(self.authorization_fact(json.loads(caps.values(self.monitor_pending['inputs'])['command'])))
            end=min(clock.evaluation_time+3600,self.expires)
            envelope=a.build_action_dependency_time_envelope_id_v01(dependency_id=prior.dependency_id,evidence_ref=prior.evidence_ref,
                content_sha256=digest,freshness_policy_id=prior.freshness_policy_id,source_provenance_refs=prior.source_provenance_refs,
                valid_from_utc=clock.evaluation_time,valid_to_utc=end)
            observation=a.build_action_dependency_current_observation_v01(dependency_id=prior.dependency_id,evidence_ref=prior.evidence_ref,
                observed_content_sha256=digest,time_envelope_id=envelope,freshness_policy_id=prior.freshness_policy_id,
                source_provenance_refs=prior.source_provenance_refs,valid_from_utc=clock.evaluation_time,valid_to_utc=end,
                observed_at_utc=clock.evaluation_time,observation_context_id=clock.evaluation_context_id)
            self.source.sample(observation)
            self.journal('PENDING_POLICY_DEPENDENCY_CHANGED',packet_id=self.monitor_pending['packet_id'],observation=plain(observation))

    def evaluate_channel(self):
        work=self.observation_work('channel')
        if work['result']['hard_critical'] and not self.signal:
            effect=self.command(dict(op='SET_LOCAL_SIGNAL_STATE',state='ON',basis_ref=c.identity('channel_result',work)),
                dict(independent_current_channels=work['result']['hard_critical'],signal_inactive=not self.signal))
            return dict(work=work,effect=effect,signal=self.read_signal())
        return dict(work=work,effect=None,signal=self.read_signal())

    def pure_consumer(self,operation,material,**kwargs):
        self.budgets.consume('pure_work',operation)
        return super().pure_consumer(operation,material,**kwargs)

    def read_reserve_series(self,source_ref,tick):
        from .events_v01 import validate,observation
        records=self.fixture.get('reserve_series')
        if records is None:
            records=[observation('reserve',row['value'],row['tick'],i+1,lineage='independent:reserve_series')
                for i,row in enumerate(self.fixture.get('reserve_series_raw',[]))]
        c.require(source_ref=='synthetic:reserve_series:v01' and len(records)==3,'reserve_series_missing')
        for row in records:
            validate(row)
            c.require(row['site']==self.fixture['site'] and row['channel']=='reserve' and row['received']<=tick,'reserve_series_source')
        return json.loads(c.canonical(records))

    def role_material(self,semantic):
        semantics.validate_bound(semantic)
        context=semantic['context'];selection=semantic['response']['diagnostic']
        c.require(semantic['request']['target_root_id']==self.root and context['policy']==self.contract,'role_current_root_policy')
        c.require(context['capabilities']==self.capabilities.snapshot(context['duty']) and context['scenario_tick']==self.tick,'role_current_context')
        c.require(all(self.book.latest.get(v['channel'])==v for v in context['sources'].values() if 'observation_id' in v),'role_current_source')
        c.require(all(v in self.frames for v in context['sources'].values() if 'sensor' in v),'role_current_projection')
        if context['duty']!='CLOUD_ENVIRONMENTAL_ANALYST':
            c.require(all(0<=self.tick-v['observed_end']<=self.contract['max_local_age_seconds']
                for v in context['sources'].values() if 'observation_id' in v),'semantic_stale_local_measurement')
        row=dict(selection=selection,semantic_ref=semantic['contribution']['contribution_id'],tick=self.tick,site=self.fixture['site'],
            observations=sorted((v for v in context['sources'].values() if 'observation_id' in v),key=lambda v:v['observation_id']),series=None)
        if context.get('investigation_contract_version'):
            row['investigation']=c.investigation(selection,context['duty'])
        return dict(selection=selection,frames=json.loads(c.canonical(self.frames)),contract=dict(self.contract),semantic_bindings=[semantic],checks=[row],phase='PLAN')

    def plan_roles(self,semantics_rows,*,fractal=False):
        c.require(type(semantics_rows) is list and bool(semantics_rows),'role_batch_required')
        # The complete batch is validated before any optional read can be authorized.
        materials=[self.role_material(row) for row in semantics_rows]
        material=dict(materials[0],semantic_bindings=[v for row in materials for v in row['semantic_bindings']],
            checks=[v for row in materials for v in row['checks']])
        semantics.validate_current(material,self)
        if fractal:
            self.budgets.consume('pure_work','CURRENT_FRACTAL_PLAN')
            execution=k.assemble(self,material);program,results,artifact=execution['program'],execution['results'],execution['artifact']
        else:
            execution=None;program,results,artifact=self.pure_consumer('sentinel.diagnostic.v01',material)
        basis=k.review_work(self,(program,results,artifact),material,
            common=execution['common'] if execution else None,
            review_bindings=((execution['obligation'],execution['source'],execution['bundle']),) if execution else ())
        if not hasattr(self,'accepted_plans'):self.accepted_plans={}
        self.accepted_plans[artifact.artifact_id]=basis
        save(self.directory/('plan_'+str(len(self.accepted_plans))+'.json'),dict(material=material,
            program=program.candidate,results=results,artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),
            root=plain(basis.review[2]),basis=k.reviewed_work_refs(basis),
            bsep=basis.common['source_context'].bsep_packet))
        return basis,execution

    def execute_role_plan(self,basis):
        output=k.validate_reviewed_work(self,basis)
        c.require(output['stage']=='PLAN','diagnostic_plan_required')
        material=json.loads(basis.material)
        if not hasattr(self,'series_materials'):self.series_materials={}
        for row in material['checks']:
            if row['selection']!='INDEPENDENT_RESERVE_SERIES':continue
            key=row['semantic_ref'];storage_key=c.identity('series_use',dict(semantic=key,dependencies=basis.dependencies.decode()))
            previous=self.series_materials.get(storage_key)
            if previous is not None:
                c.require(previous['dependencies']==basis.dependencies,'series_snapshot_changed')
                series=json.loads(previous['canonical'])
                self.journal('RECORDED_SERIES_INPUT_CONSUMED',semantic_ref=key,receipt_ref=series['receipt_ref'],creates_action=False)
            else:
                effect=self.command(dict(op='READ_RESERVE_SERIES',basis_ref=basis.artifact.artifact_id,
                    source_ref='synthetic:reserve_series:v01',tick=self.tick),dict(current_plan=True,
                    admitted_source=bool(self.fixture.get('reserve_series') or self.fixture.get('reserve_series_raw'))),accepted_work=basis)
                series=dict(json.loads(effect['output']['material']),receipt_ref=effect['receipt']['artifact_id'],
                    receipt=effect['receipt'],source_ref='synthetic:reserve_series:v01',plan_basis=k.reviewed_work_refs(basis))
                self.series_materials[storage_key]=dict(dependencies=basis.dependencies,canonical=c.canonical(series))
                self.journal('ACTUAL_REVIEWED_SERIES_READ',semantic_ref=key,receipt_ref=series['receipt_ref'],
                    plan_ref=basis.artifact.artifact_id,root=self.root,source_ref=series['source_ref'])
            row['series']=series
        material.update(phase='RESULT',accepted_plan=k.reviewed_work_refs(basis))
        semantics.validate_current(material,self)
        program,results,artifact=self.pure_consumer('sentinel.diagnostic.v01',material)
        result_basis=k.review_work(self,(program,results,artifact),material)
        output=json.loads(caps.values(results[0].result.output)['material'])
        c.require(output['semantic_refs']==[v['contribution']['contribution_id'] for v in material['semantic_bindings']],
            'actual_all_role_results_consumed')
        record=dict(material=material,program=plain(program.candidate),results=plain(results),output=output,
            work_artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),root=plain(result_basis.review[2]),routes=plain(self.routes[-1:]),
            bsep=result_basis.common['source_context'].bsep_packet,plan_basis=k.reviewed_work_refs(basis),
            plan_program=plain(basis.program.candidate),plan_bsep=basis.common['source_context'].bsep_packet,
            plan_root=plain(basis.review[2]),plan_results=plain(basis.results))
        record['role_consumptions']=[dict(semantic=v,consumed=check,result=plain(results),root=plain(result_basis.review[2]))
            for v,check in zip(material['semantic_bindings'],output['checks'],strict=True)]
        self.role_results.append(record)
        save(self.directory/('composition_'+str(len(self.role_results))+'.json'),record)
        return record

    def consume_roles(self,semantics_rows,*,fractal=False):
        basis,execution=self.plan_roles(semantics_rows,fractal=fractal)
        return self.execute_role_plan(basis),execution

    def diagnostic_roles(self,responses):
        note=self.fixture.get('maintenance_note',self.fixture['reference_note'])
        if type(note) is dict:
            c.require(note['site']==self.fixture['site'] and note['observed_at']<=note['received_at']<=self.tick,'maintenance_note_current_binding')
        collected=[]
        for intended,response in responses.items():
            material,semantic=semantics.collect(self.frames,note,self.root,
                self.source.sample().evaluation_time,controlled=response,intended_role=intended,
                capabilities=self.capabilities.snapshot(intended),observations=tuple(self.book.latest.values()),tick=self.tick,policy=self.contract)
            collected.append(semantic)
        self.consume_roles(collected)
        save(self.directory/'controlled_roles.json',self.role_results)

    def start_optional(self):
        c.require(self.capabilities.available('site_context') and self.pending_worker is None,'optional_request_not_admissible')
        old=c.canonical(dict(observations=self.book.latest,capability_revision=self.capabilities.revision,root=self.root))
        self.budgets.allocate('optional_context',2,c.digest(old));self.budgets.consume('optional_context','REQUEST_ENTER')
        self.capabilities.request('site_context',c.digest(old))
        self.optional_started=threading.Event();self.optional_release=threading.Event()
        self.pending_worker=threading.Thread(target=pending_stub,args=(old,self.directory,self.optional_started,self.optional_release,self.pending_return),
            name='sentinel-ls1-optional-immutable-worker')
        self.pending_worker.start();c.require(self.optional_started.wait(5),'optional_worker_not_started')
        self.pending_snapshot=c.canonical(self.budgets.tasks['optional_context'])
        self.journal('OPTIONAL_ACTUALLY_PENDING',context_sha256=c.digest(old),task=self.budgets.tasks['optional_context'])

    def connectivity(self,online,tick):
        self.book.advance(tick);self.tick=tick;self.capabilities.change(online)
        self.journal('CAPABILITIES_CHANGED',tick=tick,online=online,revision=self.capabilities.revision)

    def evaluate_local(self):
        assessment=self.incident.evaluate(self.book,contract=self.contract)
        if assessment['new_incident']:
            task='critical:'+self.incident.incident_id
            self.budgets.allocate(task,6,c.digest(self.book.latest))
            self.budgets.consume(task,'LOCAL_WORK_ENTER');work=self.local_work()
            self.budgets.consume(task,'ROOT_NATIVE_SIGNAL_ENTER')
            effect=self.command(dict(op='SET_LOCAL_SIGNAL_STATE',state='ON',basis_ref=c.identity('critical_witnesses',assessment)),
                dict(hard_floor=assessment['hard_critical'],current_work=work['features']['hard_critical'],single_incident=not self.read_signal()['signal']))
            self.on_effect=effect;self.on_completed=self.journal('INCIDENT_ON_COMPLETED',tick=self.tick,packet_id=effect['packet_id'])
            self.budgets.entries.append(dict(operation='NATIVE_RESULT',task=task,packet_id=effect['packet_id'],
                receipt_id=effect['receipt']['artifact_id'],host_revision=self.host.revision,root=self.root))
            if self.pending_worker is not None:
                c.require(not self.pending_return and c.canonical(self.budgets.tasks['optional_context'])==self.pending_snapshot,'pending_costs_preserved')
            self.report=dict(incident_id=self.incident.incident_id,previous_report_ref=None,classification='TEST',
                generated_at=self.tick,historical_interval=[self.tick,self.tick],source_hashes=[c.digest(v) for v in self.book.latest.values()],
                signal_receipt=effect['receipt']['artifact_id'],observations=json.loads(c.canonical(self.book.latest)))
            self.budgets.consume(task,'ROOT_NATIVE_QUEUE_ENTER')
            queued=self.command(dict(op='QUEUE_INCIDENT_REPORT',basis_ref=effect['receipt']['artifact_id'],report=self.report),
                dict(actual_on=self.read_signal()['signal'],incident_active=self.incident.state=='ACTIVE'))
            self.message=json.loads(queued['output']['material'])
        elif assessment['clearance']:
            effect=self.command(dict(op='SET_LOCAL_SIGNAL_STATE',state='OFF',basis_ref=c.identity('clearance',assessment)),
                dict(measured_clearance=assessment['clearance'],incident_active=self.incident.state=='ACTIVE',actual_signal=self.read_signal()['signal']))
            c.require(not self.read_signal()['signal'],'off_readback')
            self.incident.close(self.tick,effect['receipt']['artifact_id']);self.off_effect=effect
            save(self.directory/'clearance.json',dict(assessment=assessment,effect=effect,readback=self.read_signal()))
        self.journal('LOCAL_ASSESSMENT',tick=self.tick,assessment=assessment,incident_state=self.incident.state,signal=self.read_signal()['signal'])
        return assessment

    def release_optional(self):
        if self.pending_worker is None:return
        self.optional_release.set();self.pending_worker.join(10)
        c.require(not self.pending_worker.is_alive(),'owned_optional_not_joined')
        self.budgets.consume('optional_context','HISTORICAL_RESPONSE_RETURN')
        self.budgets.tasks['optional_context']['state']='COMPLETED_HISTORICAL_ONLY'
        self.journal('OPTIONAL_JOINED',late_response=self.pending_return,budgets=self.budgets.tasks)

    def deliver(self):
        prior=next((row for row in reversed(self.outbox.trail) if row['state']=='RECEIVED' and row['message_id']==self.message['message_id']),None)
        if prior is not None:
            ack=self.receiver.readback(self.message['message_id'])
            c.require(ack==dict(message_id=prior['message_id'],payload_sha256=prior['payload_sha256']),'duplicate_ack_mismatch')
            c.require(c.digest(self.outbox.read(prior['message_id']))==ack['payload_sha256'],'duplicate_payload_mismatch')
            self.journal('DELIVERY_DUPLICATE_CONFIRMED',ack=ack,creates_new_action=False)
            return dict(status='ALREADY_RECEIVED',ack=ack)
        return self.command(dict(op='DELIVER_INCIDENT_REPORT',basis_ref=self.message['message_id'],message_id=self.message['message_id']),
            dict(upload_current=self.capabilities.available('site_upload'),immutable_report=self.outbox.read(self.message['message_id'])==c.canonical(self.report)))

    def remember_incident(self):
        c.require(self.incident.state=='CLOSED' and not self.read_signal()['signal'],'incident_summary_closed')
        store=SentinelMemory(self.directory/'incident_drs')
        value=dict(incident_id=self.incident.incident_id,signal_on_at=self.on_completed['tick'],
                   signal_off_at=self.incident.transitions[-1]['tick'],message_id=self.message['message_id'],
                   off_receipt=self.off_effect['receipt']['artifact_id'])
        ref=store._write(self,'incident_summary',value,[c.digest(self.off_effect['receipt'])],3600)
        save(self.directory/'incident_memory_write.json',dict(record_id=ref,value=value,events=store.events))
        return ref

    def query_incident(self):
        store=SentinelMemory(self.directory/'incident_drs')
        selected=store.select(root=self.root,request=self.request,dependency=memory_dependencies(self),
            now=self.source.sample().evaluation_time,kind='incident_summary')
        c.require(selected is not None,'incident_memory_not_found')
        self.work_mode='memory_informed'
        try:work=self.pure_consumer('sentinel.information.v01',dict(summary=c.canonical(selected[0]).decode(),record_id=selected[1]['record_id']))
        finally:self.work_mode='deterministic'
        result=dict(selected=selected,events=store.events,result=plain(work[1]))
        save(self.directory/'incident_memory_query.json',result);return result
