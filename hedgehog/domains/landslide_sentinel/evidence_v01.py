"""Explicit evidence projection; no serialization of runtime Host authority."""
from dataclasses import fields, is_dataclass
import json
import os
from pathlib import Path
import time
from . import contracts_v01 as c


def plain(value):
    if value is None or type(value) in (str,int,float,bool):return value
    if type(value) in (list,tuple):return [plain(v) for v in value]
    if type(value) is dict:return {k:plain(v) for k,v in value.items()}
    c.require(is_dataclass(value) and 'SourceContext' not in type(value).__name__
        and 'Capture' not in type(value).__name__ and 'ExecutionBundle' not in type(value).__name__, 'runtime_authority_not_serializable')
    return {f.name:plain(getattr(value,f.name)) for f in fields(value)}


def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(c.canonical(plain(value))+b'\n')


def phase(directory, name, **values):
    row=dict(phase=name,monotonic=time.monotonic(),wall_epoch=time.time(),**values)
    for path in (Path(directory)/'phases.jsonl',Path(os.environ.get('LS0_PHASE_LOG',str(Path(directory)/'command_phases.jsonl')))):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
    print(json.dumps(row,sort_keys=True),flush=True)
    return row


def _package_context(rows, causal_rows, source_head, slice_id='ls0'):
    """General package construction; relationship validation is a separate public consumer."""
    from hedgehog.kernel import abi_v01 as abi, integrity_replay_v01 as integrity
    from hedgehog.evidence import sealed_evidence_profile_v01 as profile, sealed_package_v01 as package, external_anchor_v01 as anchor
    artifacts=tuple(abi.build_kernel_artifact_v01(**dict(v,trace_refs=tuple(v['trace_refs']),parent_refs=tuple(v['parent_refs']))) for v in rows)
    c.require(not abi.validate_kernel_artifact_bundle_v01(artifacts=artifacts),'safe_artifact_bundle')
    causal=tuple(abi.build_causal_consumption_ref_v01(**dict(v,trace_refs=tuple(v['trace_refs']))) for v in causal_rows)
    refs=tuple(abi.kernel_artifact_to_canonical_ref_v01(v) for v in artifacts)
    manifest=integrity.build_artifact_manifest_v01(transaction_id=artifacts[0].transaction_id,profile=integrity.build_default_seal_profile_v01(),
        artifacts=refs,dependency_edges=tuple(integrity.ArtifactDependencyEdgeV01(v.artifact_id,p) for v in artifacts for p in v.parent_refs),
        root_ownership_bindings=tuple(integrity.RootOwnershipBindingV01(v.artifact_id,v.owner_root_id) for v in artifacts),
        evidence_class_bindings=tuple(integrity.EvidenceClassBindingV01(v.artifact_id,'EVIDENCE_ONLY') for v in artifacts),
        authority_class_bindings=tuple(integrity.AuthorityClassBindingV01(v.artifact_id,v.authority_class) for v in artifacts))
    payloads=tuple((v['artifact_id'],v['payload']) for v in rows)
    verified=integrity.verify_artifact_replay_v01(manifest=manifest,payload_rows=payloads,expected_manifest_hash=manifest.manifest_hash)
    c.require(verified.replay_status=='PASS','safe_kernel_replay')
    document=dict(artifacts=rows,causal_refs=causal_rows,execution_head=source_head,
        kernel_manifest=integrity.artifact_manifest_to_plain_dict_v01(manifest),
        kernel_replay=integrity.replay_verification_result_to_plain_dict_v01(verified))
    if slice_id!='ls0':document['slice_id']=slice_id
    data=c.canonical(document)+b'\n'
    programme=profile.build_programme_evidence_identity_v01(programme_id='radiolaria_landslide_sentinel',programme_version=slice_id+'.v01')
    execution=profile.build_domain_execution_identity_v01(programme_identity=programme,domain_id='landslide_sentinel',
        execution_head=source_head,source_task_id=slice_id+'_integration',run_id=slice_id+':'+c.digest(document),report_id=c.digest(rows))
    attempt=profile.build_live_attempt_identity_v01(programme_identity=programme,domain_execution_identity=execution,
        attempt_number=1,package_id='sentinel:'+c.digest(document),logical_package_ref='packages/landslide_sentinel/'+slice_id,
        output_directory_ref='safe_package',provider_mode='deterministic_fixture',model_id='local-safe-export',expected_actor_count=1,provider_call_budget=0)
    source=profile.build_safe_source_record_v01(source_id='sentinel:source:projection',source_type='PUBLIC_SAFE_DERIVATIVE',
        evidence_class='EXECUTED_DETERMINISTIC_RUNTIME',canonical_projection=document,media_type='application/json',trace_refs=(manifest.manifest_hash,),
        contains_raw_prompt=False,contains_raw_provider_response=False,secret_scan_passed=True,
        observed_provider_call_count=0,observed_network_call_count=0,observed_gemini_call_count=0,real_world_effects_count=0)
    integrity_source=profile.build_safe_source_record_v01(source_id='sentinel:source:integrity',source_type='PUBLIC_KERNEL_REPLAY',
        evidence_class='CRYPTOGRAPHIC_INTEGRITY',canonical_projection=document['kernel_replay'],media_type='application/json',
        trace_refs=(manifest.manifest_hash,),contains_raw_prompt=False,contains_raw_provider_response=False,secret_scan_passed=True,
        observed_provider_call_count=0,observed_network_call_count=0,observed_gemini_call_count=0,real_world_effects_count=0)
    records=tuple(profile.build_evidence_artifact_record_v01(artifact_id=v.artifact_id,artifact_type=v.artifact_type,
        evidence_class='EXECUTED_DETERMINISTIC_RUNTIME',source_record_ids=(source.source_record_id,),
        canonical_projection=abi.kernel_artifact_to_plain_dict_v01(v),authority_class='EVIDENCE_ONLY',owner_root_id=v.owner_root_id,
        trace_refs=v.trace_refs,created_authority_count=0,created_permission_count=0,real_world_effects_count=0) for v in artifacts)
    projection=profile.build_domain_evidence_projection_v01(programme_identity=programme,domain_execution_identity=execution,
        attempt_identity=attempt,source_records=(source,integrity_source),artifact_records=records,kernel_artifact_refs=refs,causal_consumption_refs=causal,
        evidence_refs=(manifest.manifest_hash,c.digest(rows)),limitation_refs=('SAFE_DERIVED_NOT_NATIVE_REPLAY','TEST_SUPPLIED_PIN_PENDING_REVIEW',
            'EXPORT_AND_REPLAY_COUNTS_ARE_NOT_HISTORICAL_LIVE_COUNTS','STRUCTURAL_LINKS_NOT_SENSOR_TRUTH'))
    file_record=package.build_safe_file_record_v01(logical_path='projection.json',media_type='application/json',content_bytes=data,
        evidence_class=source.evidence_class,source_record_ids=(source.source_record_id,integrity_source.source_record_id),terminal_newline_required=True,secret_scan_passed=True)
    sealed=package.build_sealed_package_manifest_v01(domain_projection=projection,safe_file_records=(file_record,),safe_file_contents=(data,),kernel_manifest_hash=manifest.manifest_hash)
    context=dict(manifest=sealed,domain_projection=projection,safe_file_contents=(data,))
    publication=anchor.build_external_anchor_publication_v01(**context,publication_base_head=source_head)
    return context,publication,document,artifacts,causal


def write_package(directory, rows, causal_rows, source_head, slice_id='ls0'):
    """Write a new evidence-only package; never grant present execution authority."""
    from hedgehog.kernel import abi_v01 as abi
    context,publication,document,artifacts,causal=_package_context(rows,causal_rows,source_head,slice_id)
    c.require(not abi.validate_causal_consumption_bundle_v01(artifacts=artifacts,causal_refs=causal),'safe_causal_relationship')
    return _persist_package(directory,context,publication,document)


def _persist_package(directory,context,publication,document):
    from hedgehog.evidence import sealed_package_v01 as package,external_anchor_v01 as anchor
    target=Path(directory);c.require(not target.exists(),'package_destination_exists');target.mkdir(parents=True)
    save(target/'projection.json',document)
    save(target/'manifest.json',package.sealed_package_manifest_to_plain_dict_v01(context['manifest'],
        domain_projection=context['domain_projection'],safe_file_contents=context['safe_file_contents']))
    save(target/'publication.json',anchor.external_anchor_publication_to_plain_dict_v01(publication,**context))
    return dict(publication_id=publication.anchor_publication_id,pin_provenance='TEST_SUPPLIED_PIN',review='PENDING_REVIEW',
                authority='EVIDENCE_ONLY',directory=str(target))


def verify_package(directory, expected_pin):
    """Disk-only reconstruction and public pin, replay, and causal validation."""
    from hedgehog.kernel import abi_v01 as abi
    from hedgehog.evidence import sealed_package_v01 as package,external_anchor_v01 as anchor,sealed_replay_evidence_v01 as replay
    target=Path(directory)
    c.require(target.is_dir() and not target.is_symlink(),'package_directory')
    c.require({p.name for p in target.iterdir()}=={'projection.json','manifest.json','publication.json'},'package_exact_coverage')
    def reopen():
        c.require(all(not p.is_symlink() and p.is_file() for p in target.iterdir()),'package_regular_files')
        raw=(target/'projection.json').read_bytes();data=json.loads(raw)
        c.require(raw==c.canonical(data)+b'\n','package_canonical_bytes')
        context,publication,doc,artifacts,causal=_package_context(data['artifacts'],data['causal_refs'],data['execution_head'],data.get('slice_id','ls0'))
        c.require(data==doc,'package_kernel_material')
        manifest=package.sealed_package_manifest_to_plain_dict_v01(context['manifest'],domain_projection=context['domain_projection'],safe_file_contents=context['safe_file_contents'])
        c.require((target/'manifest.json').read_bytes()==c.canonical(manifest)+b'\n','package_covered_bytes_changed')
        pub=anchor.external_anchor_publication_to_plain_dict_v01(publication,**context)
        c.require((target/'publication.json').read_bytes()==c.canonical(pub)+b'\n','package_publication_changed')
        return context,publication,artifacts,causal
    context,publication,artifacts,causal=reopen()
    verified=anchor.build_anchored_package_verification_v01(anchor_publication=publication,**context,supplied_anchor_publication_id=expected_pin)
    c.require(verified.verification_status=='ANCHORED_PASS','external_anchor_mismatch')
    relationship=abi.validate_causal_consumption_bundle_v01(artifacts=artifacts,causal_refs=causal)
    c.require(not relationship,'public_causal_relationship:'+repr(relationship))
    rebuilt,_,_,_=reopen()
    args=dict(source_manifest=context['manifest'],source_domain_projection=context['domain_projection'],source_safe_file_contents=context['safe_file_contents'],
        anchor_publication=publication,anchored_verification=verified,supplied_anchor_publication_id=expected_pin,
        reconstructed_manifest=rebuilt['manifest'],reconstructed_domain_projection=rebuilt['domain_projection'],reconstructed_safe_file_contents=rebuilt['safe_file_contents'])
    result=replay.build_sealed_replay_evidence_v01(**args,evidence_refs=('sentinel:disk_reopen',expected_pin))
    c.require(result.replay_status=='PASS' and not replay.validate_sealed_replay_evidence_v01(result,**args),'public_sealed_replay')
    return dict(status='PASS',pin_provenance='TEST_SUPPLIED_PIN',review='PENDING_REVIEW',
        anchor=anchor.anchored_package_verification_to_plain_dict_v01(verified,anchor_publication=publication,**context,supplied_anchor_publication_id=expected_pin),
        replay=replay.sealed_replay_evidence_to_plain_dict_v01(result,**args),causal_errors=relationship,
        scope='SAFE_DERIVED_ONLY',provider_calls=0,sensor_calls=0,configuration_calls=0,signal_calls=0,report_effect_calls=0)


def export_run(session, source_head):
    return export_recorded_run(session.directory,source_head)


def export_recorded_run(directory, source_head):
    """Derive portable evidence from completed records, never restore a Host."""
    from hedgehog.kernel import abi_v01 as abi
    directory=Path(directory)
    names=('semantic_work.json','new_configuration.json','critical_pending.json','phases.jsonl')
    c.require(all((directory/name).is_file() and not (directory/name).is_symlink() for name in names),'recorded_inputs_regular')
    sources={name:(directory/name).read_bytes() for name in names}
    semantic=json.loads(sources['semantic_work.json']);configuration=json.loads(sources['new_configuration.json'])
    critical=json.loads(sources['critical_pending.json']);events=[json.loads(v) for v in sources['phases.jsonl'].splitlines()]
    output=json.loads(configuration['effect']['output']['material'])
    intakes=[v for v in events if v['phase']=='ACTUAL_LOCAL_INTAKE']
    c.require(intakes and intakes[-1]['cadence_seconds']==output['cadence_seconds'],'recorded_intake_relationship')
    c.require(configuration['consumed']['recomputed_result_ref'] and critical['final_signal'] and critical['worker_joined'],'recorded_completion_required')
    documents=[dict(kind='diagnostic',native_work_ref=semantic['work_artifact']['artifact_id'],
                    selection=semantic['semantic']['response']['diagnostic'],actual_mode=semantic['semantic']['actual_mode'],
                    source_documents={name:c.digest(data) for name,data in sources.items()}),
               dict(kind='current_configuration',native_effects=[configuration['effect']['receipt']['artifact_id'],critical['effect']['receipt']['artifact_id']],
                    cadence=output['cadence_seconds'],consumed_delta=configuration['consumed'],intakes=intakes)]
    rows=[]
    for document in documents:
        obj=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('safe_projection',document),artifact_type='SemanticEvidence',
            schema_version='v1',transaction_id='sentinel:safe_export',owner_root_id='sentinel:evidence_custodian',
            source_component='sentinel_safe_export',authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',payload=dict(safe_document=document),
            trace_refs=(c.digest(document),),parent_refs=tuple(v['artifact_id'] for v in rows[-1:]),
            time_envelope=dict(pt_created_at='2026-09-14T00:00:00Z',kt_asof='2026-09-14T00:00:00Z',et_observed_at=None,
                ct_session_anchor='sentinel:historical_export',ttl_seconds=0,freshness_class='static',valid_from=None,valid_to=None))
        rows.append(abi.kernel_artifact_to_plain_dict_v01(obj))
    causal=abi.build_causal_consumption_ref_v01(producer_actor_id='sentinel_safe_export',source_artifact_id=rows[0]['artifact_id'],
        output_field='/safe_document',consumer_component='sentinel_safe_export',downstream_artifact_id=rows[1]['artifact_id'],
        decision_effect='Evidence projection relationship only',disposition='USED',reason_code='used:sentinel_safe_derivation',trace_refs=(semantic['work_artifact']['artifact_id'],))
    return write_package(directory/'safe_package',rows,[plain(causal)],source_head)


class BoundaryObserver:
    """Passive code-object counters, not OS-wide transport or sensor monitoring."""
    def __init__(self):
        self.counts={};self.codes={};self.tool=3

    def __enter__(self):
        import sys
        from .monitoring_runtime_v01 import Sentinel,ControlledEpisode,SentinelMemory
        from .events_v01 import CapabilityState
        from .semantic_adapter_v01 import GeminiHarness
        from .outbox_v01 import Outbox,Receiver
        from hedgehog import local_drs_resolver as resolver,work_execution_host_v01 as host
        from hedgehog import drs_memory_resolution_v01 as memory
        from hedgehog.kernel import continuous_delta_runtime_v01 as delta,fractal_runtime_v02 as fractal
        from google.genai.models import Models,AsyncModels
        functions=dict(harness_attempt=GeminiHarness.respond,harness_transport=Models.generate_content,
            harness_async_transport=AsyncModels.generate_content,site_request=CapabilityState.request,
            sensor_attempt=Sentinel.intake,local_work=Sentinel.pure_consumer,drs_search=resolver.resolve_semantic_candidates,
            drs_write=resolver.write_semantic_record,drs_descent=memory.execute_local_memory_descent_v01,
            mock_effect=ControlledEpisode.execute_effect,series_read=ControlledEpisode.read_reserve_series,native_dispatch=host.dispatch_current_action_v01,
            outbox_queue=Outbox.queue,outbox_deliver=Outbox.deliver,receiver_receive=Receiver.receive,
            public_D=fractal.run_fractal_runtime_v02,public_E=delta.run_continuous_delta_runtime_v01)
        self.codes={fn.__code__:name for name,fn in functions.items()}
        self.counts={name:0 for name in functions}
        self.counts.update(sensor_completed=0,site_completed=0,harness_completed=0,configuration_effect=0,signal_effect=0,report_effect=0,series_effect=0)
        sys.monitoring.use_tool_id(self.tool,'sentinel-boundaries')
        def enter(code,offset):
            name=self.codes[code];self.counts[name]+=1
            if name=='mock_effect':
                frame=sys._getframe(1);inputs=frame.f_locals['inputs'];op=json.loads(inputs['command'])['op']
                key=('series_effect' if op=='READ_RESERVE_SERIES' else 'configuration_effect' if op=='APPLY_MONITORING_CONFIG' else ('signal_effect' if op=='SET_LOCAL_SIGNAL_STATE' else 'report_effect'))
                self.counts[key]+=1
        def returned(code,offset,value):
            if self.codes[code]=='sensor_attempt' and value is not None:self.counts['sensor_completed']+=1
            if self.codes[code]=='site_request':self.counts['site_completed']+=1
            if self.codes[code]=='harness_attempt':self.counts['harness_completed']+=1
        for event,fn in ((sys.monitoring.events.PY_START,enter),(sys.monitoring.events.PY_RETURN,returned)):
            sys.monitoring.register_callback(self.tool,event,fn)
        for code in self.codes:sys.monitoring.set_local_events(self.tool,code,sys.monitoring.events.PY_START|sys.monitoring.events.PY_RETURN)
        return self

    def snapshot(self):return dict(self.counts,site_rejected=self.counts['site_request']-self.counts['site_completed'],
        harness_rejected=self.counts['harness_attempt']-self.counts['harness_completed'])

    def delta(self,before):return {k:v-before[k] for k,v in self.snapshot().items()}

    def __exit__(self,*args):
        import sys
        for code in self.codes:sys.monitoring.set_local_events(self.tool,code,0)
        sys.monitoring.free_tool_id(self.tool)


def export_story(directory,source_head):
    from datetime import datetime,timezone
    from hedgehog.kernel import abi_v01 as abi
    directory=Path(directory);story=json.loads((directory/'story.json').read_bytes())
    sources={p.name:c.digest(p.read_bytes()) for p in directory.glob('*.json') if p.is_file()}
    documents=[dict(kind='LS1_SOURCE_BOUND_CONTROLLED_STORY',source_documents=sources,root=story['root'],modes=story['modes']),
               dict(kind='LS1_EFFECT_AND_CLEARANCE_DERIVATIVE',story=story)]
    rows=[];created=datetime.now(timezone.utc).isoformat()
    for document in documents:
        obj=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('ls1_safe_projection',document),artifact_type='SemanticEvidence',
            schema_version='v1',transaction_id='sentinel:ls1_safe_export',owner_root_id='sentinel:evidence_custodian',
            source_component='sentinel_safe_export',authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',payload=dict(safe_document=document),
            trace_refs=(c.digest(document),),parent_refs=tuple(v['artifact_id'] for v in rows[-1:]),
            time_envelope=dict(pt_created_at=created,kt_asof=created,et_observed_at=None,ct_session_anchor='sentinel:ls1_export',
                ttl_seconds=0,freshness_class='static',valid_from=None,valid_to=None))
        rows.append(abi.kernel_artifact_to_plain_dict_v01(obj))
    ref=abi.build_causal_consumption_ref_v01(producer_actor_id='sentinel_safe_export',source_artifact_id=rows[0]['artifact_id'],
        output_field='/safe_document',consumer_component='sentinel_safe_export',downstream_artifact_id=rows[1]['artifact_id'],
        decision_effect='Safe evidence derivative only',disposition='USED',reason_code='used:ls1_story_sources',trace_refs=(story['root'],))
    return write_package(directory/'safe_package',rows,[plain(ref)],source_head,'ls1')
