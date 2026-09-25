"""One persistent PersonalRoot and finite current commands over owned resources."""
import base64
import json
import os
from pathlib import Path
import secrets
import stat as stat_types
import threading
import time
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import abi_v01 as abi
from . import contracts_v01 as c, capability_registry_v01 as caps, kernel_adapter_v01 as kernel
from .semantic_adapter_v01 import collect
from .semantic_roles_v01 import ControlledProvider
from .local_services_v01 import Service
from .media_v01 import privacy_policy, validate_transfer


class Workspace:
    def __init__(self, directory, assets, request=c.REQUEST_A, provider=None, lifetime=1200, *, media=None, personal_root=None):
        self.directory=Path(directory)
        self.directory.mkdir(parents=True,exist_ok=False,mode=0o700)
        # Opaque alphabetic IDs cannot accidentally look like payment data in B's safe references.
        alphabet=str.maketrans('0123456789abcdef','abcdefghijklmnop')
        self.id='ews:session:'+secrets.token_hex(12).translate(alphabet)
        self.root='root:ews:personal:'+secrets.token_hex(8).translate(alphabet)
        if personal_root is not None:
            c.require(type(personal_root) is str and personal_root.startswith('root:ews:personal:') and len(personal_root)<=128,'personal_root_identity')
            self.root=personal_root
        self.request=request
        from .media_v01 import load_media
        self.media_fixture=None if media is None else load_media(media)
        self.media_review=None
        self.media_delta=None
        self.media_state=dict(status='NOT_REQUESTED',audio='NOT_ACTIVATED',position=0,frames=0,samples=0)
        self.producer_counts=dict(photo_preview=0,media_contract=0,delta=0)
        self.media_stop=threading.Event()
        self.media_thread=None
        self.media_events=[]
        self.media_snapshot=None
        self.audio_fault=None
        self.audio_loss=None
        self.lock=threading.RLock()
        self.source=kernel.CurrentSource()
        self.expires=self.source.epoch+lifetime
        self.deadline=self.source.started+lifetime
        self.version=0
        self.status='PREPARED'
        self.revoked=False
        self.index=0
        self.assets={f'asset:{i+1}':Path(p).resolve() for i,p in enumerate(assets)}
        c.require(0<len(self.assets)<=6 and all(p.is_file() and not p.is_symlink() for p in self.assets.values()),'asset_inventory')
        self.source_hashes={n:c.digest(p.read_bytes()) for n,p in self.assets.items()}
        self.edits={n:dict(rating=0,selected=False,exposure=0,crop='ORIGINAL') for n in self.assets}
        self.pending=None
        self.approvals={}
        self.saved=None
        self.write_outcome='NOT_STARTED'
        self.services=[]
        self.resource_plan={role:secrets.token_hex(16) for role in ('media','display','controls','sidecar')}
        self.owned={}
        self.executed={}
        self.command_authority=None
        self.history=[]
        self.timings=[]
        self.cleanup_report=None
        self.preview=None
        self.privacy_transfers=[]
        self.last_activity=time.monotonic()
        self.catalogue=caps.catalogue(self.root,self.id)
        if self.media_fixture is not None:
            self.catalogue+=(caps.admit(self.root,'ews.media_contract.v01',caps.execute_media_contract_v01),)
            self.resource_plan['audio']=secrets.token_hex(16)
        self.host=hosts.build_root_work_execution_host_v01(owning_root_id=self.root,registry=action.build_empty_action_commit_packet_registry_v02(),
            catalogue=self.catalogue,packet_bindings=(),current_dependency_observations=(),logical_time_bridge=self.source.snapshot.logical_time_bridge,trusted_source=self.source)
        start=time.monotonic()
        provider=provider or ControlledProvider()
        responses,self.captures,source,self.route_review=collect(self,provider)
        self.semantic_responses=responses
        self.mode=provider.mode
        self.program,self.work_results,self.work_artifact=kernel.materialize(self,responses,source)
        self.contract=json.loads(caps.values(self.work_results[-1].result.output)['material'])
        c.require('media' not in self.contract or self.media_fixture is not None,'requested_media_missing')
        privacy_policy(self.contract['minimize'])
        self.allowed=tuple(self.contract['commands'])+('OPEN','REQUEST_SAVE','SAVE','END')
        self.timings.append(dict(phase='semantics_and_work',seconds=time.monotonic()-start))
        (self.directory/'cache').mkdir(mode=0o700)
        (self.directory/'output').mkdir(mode=0o700)
        (self.directory/'logs').mkdir(mode=0o700)

    def state(self):
        with self.lock:
            # Informational currentness only: no source I/O, renewal, packet or cleanup.
            reason=None
            try:
                self.current()
            except ValueError as exc:
                reason=str(exc)
            current=reason is None
            if current and self.media_review is not None:
                self._observe_audio_liveness('STATE')
            status=self.status
            if status in ('PREPARED','ACTIVE') and not current:
                status='REVOKED' if self.revoked else 'EXPIRED'
            allowed=[]
            approval_available=current and status=='ACTIVE' and self.pending is not None and self.saved is None
            if current:
                allowed=['OPEN'] if status=='PREPARED' else [op for op in self.allowed if op!='OPEN']
                if self.saved is not None or not any(edit['selected'] for edit in self.edits.values()):
                    allowed=[op for op in allowed if op!='REQUEST_SAVE']
                if not approval_available or not any(not a['used'] and a['candidate']==self.pending
                    for a in self.approvals.values()):
                    allowed=[op for op in allowed if op!='SAVE']
                if self.media_review is None:
                    allowed=[op for op in allowed if op not in ('PLAY','PAUSE','SEEK','REVIEW_MEDIA')]
                elif self.audio_fault is not None or (self.audio_loss is not None and (self.media_delta is None or self.media_review['output']['audio_policy']=='REQUIRE_AUDIO')):
                    allowed=[op for op in allowed if op not in ('PLAY','REVIEW_MEDIA')]
            return dict(session=self.id,version=self.version,status=status,lifecycle_status=self.status,
                current=current,current_reason=reason,mode=self.mode,index=self.index,
                assets=[dict(asset=n,**self.edits[n]) for n in self.assets],allowed=allowed,
                preview=self.preview if current and status=='ACTIVE' else None,
                pending=self.pending if approval_available else None,saved=self.saved,expires=self.expires,root=self.root,
                owner_approval_available=approval_available,owner_cleanup_available=self.cleanup_report is None,
                owner_audio_action=self._owner_audio_action(current),
                cleanup=self.cleanup_report,local_effects=len(self.executed),active_classes=self.contract['active_classes'],
                media=dict(self.media_state) if 'media' in self.contract else None)

    def _owner_audio_action(self, current):
        """Read-side UI information, never a continuation or action grant."""
        if not current or self.status!='ACTIVE' or self.cleanup_report is not None:
            return None
        if 'media' not in self.contract or self.media_review is None or self.audio_loss is not None or self.media_delta is not None:
            return None
        output=self.media_review['output']
        if not output['audio'] or output['audio_policy'] not in ('SILENT_CONTINUE','REQUIRE_AUDIO'):
            return None
        audio=next((s for s in self.services if s.role=='audio'),None)
        if audio is None:
            return None
        if self.audio_fault is not None:
            if self.audio_fault['kind']=='OWNED_PROCESS_EXIT' and audio.process.poll() is not None and self.media_state['audio']=='UNAVAILABLE':
                return 'CONTINUE_AFTER_LOSS'
            return None
        if self.media_state['audio']=='AVAILABLE' and audio.process.poll() is None:
            return 'DISCONNECT'
        return None

    def journal(self,phase,**values):
        with (self.directory/'phases.jsonl').open('ab') as stream:
            stream.write(c.canonical(dict(phase=phase,monotonic=time.monotonic(),session=self.id,version=self.version,
                host_revision=self.host.revision,**values))+b'\n')

    def current(self):
        c.require(not self.revoked and self.status in ('PREPARED','ACTIVE'), 'workspace_not_current')
        now=self.source.epoch+int(time.monotonic()-self.source.started)+self.source.offset
        c.require(time.monotonic()<self.deadline and now<self.expires,'workspace_expired')
        if hasattr(self,'contract') and self.contract['cleanup']=='on_end_and_idle':
            c.require(time.monotonic()-self.last_activity<300,'workspace_idle_expired')

    def validate_effect(self, values):
        c.exact(values,('command','session','version'))
        self.current()
        c.require(values['session']==self.id and type(values['version']) is int and values['version']==self.version,'current_session_version')
        command=c.command(json.loads(values['command']),self.allowed)
        op=command['op']
        c.require((op=='OPEN' and self.status=='PREPARED') or (op!='OPEN' and self.status=='ACTIVE'),'workspace_operation_state')
        if op=='SAVE':
            approval=self.approvals.get(command['value'])
            c.require(approval is not None and not approval['used'] and self.pending is not None and self.saved is None,'save_approval_current')
            c.require(approval['candidate']==self.pending and approval['candidate']==self.save_candidate(),'save_approval_exact_content')
        if op=='REQUEST_SAVE':
            c.require(self.saved is None,'sidecar_already_written')
            self.save_candidate()
        if op in ('PLAY','PAUSE','SEEK','REVIEW_MEDIA'):
            c.require(self.media_review is not None,'media_requires_actual_D_review')
            if op in ('PLAY','REVIEW_MEDIA'):
                self._check_audio_current('COMMAND')
            if op in ('PLAY','REVIEW_MEDIA') and self.audio_loss is not None:
                c.require(self.media_delta is not None,'audio_loss_requires_current_E')
                c.require(self.media_review['output']['audio_policy']=='SILENT_CONTINUE','speech_review_audio_unavailable')
        c.require(all(c.digest(p.read_bytes())==self.source_hashes[n] for n,p in self.assets.items()),'original_source_changed')

    def command(self, op, value=None):
        with self.lock:
            started=time.monotonic()
            command=c.command(dict(op=op,value=value),self.allowed)
            values=dict(command=c.canonical(command).decode(),session=self.id,version=self.version)
            self.validate_effect(values)
            self.journal('COMMAND_START',op=op)
            token=caps.EXECUTION.set(self)
            try:
                result=kernel.dispatch(self,command,dict(current_scope=values['session']==self.id and values['version']==self.version,
                    typed_command=c.command(command,self.allowed)==command,
                    no_source_write=not self.contract['source_write'],no_publication=not self.contract['publication'],
                    separate_save=op!='SAVE' or value in self.approvals))
                self.history.append(result)
                self.last_activity=time.monotonic()
                self.journal('COMMAND_RETURN',op=op,packet_id=result['packet_id'])
                return self.state()
            except BaseException as exc:
                self.journal('COMMAND_EXCEPTION',op=op,error_type=type(exc).__name__,reason=str(exc))
                if op=='OPEN':
                    self.close('PARTIAL_ACTIVATION_ROLLBACK')
                raise
            finally:
                caps.EXECUTION.reset(token)
                self.timings.append(dict(phase='command:'+op,seconds=time.monotonic()-started,version=self.version))

    def _preview(self):
        self.producer_counts['photo_preview']+=1
        asset=tuple(self.assets)[self.index]
        edit=self.edits[asset]
        response=self.services[0].rpc('render',dict(asset=asset,exposure=edit['exposure'],crop=edit['crop'],preview=self.contract['preview']))
        minimize=privacy_policy(self.contract['minimize'])
        png=validate_transfer(response,minimize,('png','sha256','asset','session'))
        c.require(response['session']==self.id and response['asset']==asset,'render_source_binding')
        if minimize=='preview_only':
            c.require(all(response['derived'][key]==value for key,value in
                dict(exposure=edit['exposure'],crop=edit['crop'],preview=self.contract['preview']).items()),'render_transform_binding')
        ref=c.identity('frame',dict(session=self.id,version=self.version,asset=asset,sha256=response['sha256']))
        transfer=dict(png=response['png'],sha256=response['sha256'],frame_ref=ref)
        if minimize=='preview_only':
            transfer['derived']=dict(response['derived'])
        validate_transfer(transfer,minimize,('png','sha256','frame_ref'))
        receipt=self.services[1].rpc('put',transfer)
        c.exact(receipt,('frame_ref','sha256','session','minimize','transfer_fields','transfer_sha256'),'display_receipt_fields')
        c.require(receipt==dict(frame_ref=ref,sha256=response['sha256'],session=self.id,minimize=minimize,
            transfer_fields=sorted(transfer),transfer_sha256=c.digest(transfer)),'display_transfer_binding')
        self.privacy_transfers.append(dict(version=self.version,minimize=minimize,contract_sha256=c.digest(self.contract),
            media_fields=sorted(response),media_sha256=c.digest(response),display_fields=sorted(transfer),
            display_sha256=c.digest(transfer),display_receipt_sha256=c.digest(receipt),png_sha256=c.digest(png),
            png_metadata='ABSENT_VERIFIED',derived_fields=sorted(transfer.get('derived',{}))))
        path=self.directory/'cache'/f'preview_{self.version:04d}.png'
        with path.open('xb') as stream:
            stream.write(png)
        stat=path.stat()
        self.owned[path]=(stat.st_dev,stat.st_ino,c.digest(png))
        self.preview=dict(frame_ref=ref,sha256=response['sha256'],asset=asset,version=self.version)

    def execute_effect(self, values, invocation_id):
        self.validate_effect(values)
        authority=self.command_authority
        now=self.source.epoch+int(time.monotonic()-self.source.started)+self.source.offset
        c.require(authority is not None and authority['inputs_sha256']==c.digest(values)
            and now<authority['expires'],'finite_packet_expired_before_effect')
        command=json.loads(values['command'])
        op,v=command['op'],command['value']
        if op=='OPEN':
            try:
                self.services.append(Service('media',self.id,self.deadline,self.directory/'logs',
                    {n:[str(p),self.source_hashes[n]] for n,p in self.assets.items()},nonce=self.resource_plan['media'],
                    minimize=self.contract['minimize'],preview=self.contract['preview']))
                self.services.append(Service('display',self.id,self.deadline,self.directory/'logs',nonce=self.resource_plan['display'],
                    minimize=self.contract['minimize'],preview=self.contract['preview']))
                if self.contract.get('media',{}).get('audio'):
                    import wave
                    with wave.open(str(self.media_fixture['audio']),'rb') as stream:pcm=stream.readframes(64000)
                    self.services.append(Service('audio',self.id,self.deadline,self.directory/'logs',nonce=self.resource_plan['audio'],
                        pcm_chunks=[c.digest(pcm[i:i+8000]) for i in range(0,len(pcm),8000)]))
                    self.media_state.update(status='UNREVIEWED',audio='AVAILABLE')
                self.status='ACTIVE'
            except BaseException:
                self.close('PARTIAL_ACTIVATION_ROLLBACK')
                raise
        elif op in ('NEXT','PREVIOUS'):
            self.index=(self.index+(1 if op=='NEXT' else -1))%len(self.assets)
        elif op in ('RATE','SELECT','EXPOSURE','CROP'):
            self.edits[tuple(self.assets)[self.index]][dict(RATE='rating',SELECT='selected',EXPOSURE='exposure',CROP='crop')[op]]=v
        elif op in ('PLAY','PAUSE','SEEK','REVIEW_MEDIA'):
            self.execute_media(op,v,invocation_id,authority['expires'])
        elif op=='SAVE':
            approved=self.approvals[v]
            body=c.canonical(approved['candidate']['content'])+b'\n'
            path=self.directory/'output'/'selection.json'
            self.write_outcome='STARTED'
            try:
                with path.open('xb') as stream:
                    stream.write(body)
                    stream.flush()
                    os.fsync(stream.fileno())
            except BaseException:
                self.write_outcome='UNCERTAIN_NO_AUTOMATIC_RETRY'
                self.status='WRITE_UNCERTAIN'
                raise
            approved['used']=True
            self.write_outcome='WRITTEN_ONCE'
            self.saved=dict(slot='selection.json',sha256=c.digest(body),bytes=len(body),approval=v)
        self.version+=1
        if op in ('OPEN','NEXT','PREVIOUS','EXPOSURE','CROP'):
            try:
                self._preview()
            except BaseException:
                self.status='PREVIEW_UNAVAILABLE'
                raise
        if op=='REQUEST_SAVE':
            c.require(self.saved is None,'sidecar_already_written')
            self.pending=self.save_candidate()
        elif op!='SAVE':
            self.pending=None
        if op=='END':
            self.close('END')
        result=dict(session=self.id,version=self.version,status=self.status,op=op,
            frame_ref=None if self.preview is None else self.preview['frame_ref'],saved=self.saved)
        self.executed[invocation_id]=result
        return result

    def save_candidate(self):
        selected=[dict(asset=n,source_sha256=self.source_hashes[n],**e) for n,e in self.edits.items() if e['selected']]
        c.require(bool(selected),'select_at_least_one_photo')
        content=dict(version=c.VERSION,session=self.id,selection=selected)
        candidate=dict(session=self.id,version=self.version,slot='selection.json',content=content,bytes_sha256=c.digest(c.canonical(content)+b'\n'))
        return candidate

    def validate_frame(self,ref):
        self.current()
        c.require(self.preview is not None and ref==self.preview['frame_ref'],'frame_current_binding')
        asset=self.preview['asset']
        c.require(c.digest(self.assets[asset].read_bytes())==self.source_hashes[asset],'frame_source_changed')

    def approve(self, candidate, *, actor='SCRIPTED_OWNER_CONFIRMATION'):
        with self.lock:
            self.current()
            c.require(actor in ('SCRIPTED_OWNER_CONFIRMATION','MANUAL_OWNER_CONFIRMATION'),'owner_confirmation_actor')
            c.require(self.pending is not None and c.canonical(candidate)==c.canonical(self.pending)==c.canonical(self.save_candidate()),'approval_candidate_changed')
            ref=c.identity('approval',dict(candidate=candidate,actor=actor))
            self.approvals[ref]=dict(candidate=json.loads(c.canonical(candidate)),actor=actor,used=False)
            return ref

    def close(self, reason='RESOURCE_OWNER_FINALIZER'):
        with self.lock:
            if self.cleanup_report is not None:
                return self.cleanup_report
            start=time.monotonic()
            self.status='CLOSING'
            self.media_stop.set()
            if self.media_thread is not None:
                self.media_thread.join(timeout=12)
                c.require(not self.media_thread.is_alive(),'finite_media_stop_not_completed')
            processes=[service.close() for service in reversed(self.services)]
            self.media_snapshot=None
            removed,foreign=[],[]
            for path,expected in self.owned.items():
                try:
                    stat=path.lstat()
                except FileNotFoundError:
                    continue
                except OSError:
                    foreign.append(path.name)
                    continue
                try:
                    if stat_types.S_ISREG(stat.st_mode) and (stat.st_dev,stat.st_ino,c.digest(path.read_bytes()))==expected:
                        path.unlink()
                        removed.append(path.name)
                    else:
                        foreign.append(path.name)
                except OSError:
                    foreign.append(path.name)
            self.status='CLOSED_SUCCESS' if not foreign and all(p['reaped'] for p in processes) else 'CLEANUP_INCOMPLETE'
            self.cleanup_report=dict(reason=reason,processes=processes,removed=removed,foreign_preserved=foreign,
                retained_reason='OWNERSHIP_OR_CONTENT_CHANGED_OR_UNVERIFIABLE_NOT_REMOVED' if foreign else None,
                status=self.status,seconds=time.monotonic()-start,authority='INITIAL_RESOURCE_OWNER_CLEANUP_OBLIGATION',
                boundary='finite synchronous image/IPC invocation; no asynchronous preemption claim')
            return self.cleanup_report

    def media_dependency(self):
        return dict(fixture=None if self.media_fixture is None else c.digest(self.media_fixture['manifest']),
            audio_resource=self.resource_plan.get('audio'),audio_available=self.audio_loss is None and
                any(s.role=='audio' and s.process.poll() is None for s in self.services),
            reviewed_output=None if self.media_review is None else self.media_review['results'][0].result.result_id,
            delta_result=None if self.media_delta is None else self.media_delta['consumed']['delta_result_ref'])

    def photo_frame(self, ref):
        self.validate_frame(ref)
        path=self.directory/'cache'/f"preview_{self.preview['version']:04d}.png"
        data=path.read_bytes()
        c.require(c.digest(data)==self.preview['sha256'],'current_photo_bytes')
        return data

    def media_frame(self, ref):
        self.current()
        snapshot=self.media_snapshot
        c.require(self.status=='ACTIVE' and snapshot is not None and ref==snapshot[0],'current_media_frame')
        _,sha,data=snapshot
        c.require(type(data) is bytes and c.digest(data)==sha,'current_media_bytes')
        return data

    def _observe_audio_liveness(self, boundary):
        """Owned Popen observation only; no source refresh, permission or D/E call."""
        if not self.media_review or not self.media_review['output']['audio'] or self.audio_loss is not None:
            return
        audio=next((s for s in self.services if s.role=='audio'),None)
        code=None if audio is None else audio.process.poll()
        if audio is not None and code is None:
            return
        if self.audio_fault is None:
            self.audio_fault=dict(boundary=boundary,kind='OWNED_PROCESS_EXIT' if audio else 'OWNED_PROCESS_MISSING',
                returncode=code,deadline_reached=time.monotonic()>=self.deadline,
                resource=None if audio is None else audio.nonce,monotonic=time.monotonic())
        self.media_stop.set()
        self.media_state.update(audio='UNAVAILABLE',status='AUDIO_UNAVAILABLE_PAUSED',reason='Audio unavailable; current continuation required')

    def _check_audio_current(self, boundary):
        self._observe_audio_liveness(boundary)
        c.require(self.audio_fault is None,'audio_unavailable_requires_current_continuation')
        if self.audio_loss is not None:
            c.require(self.media_delta is not None,'audio_loss_requires_current_E')
            c.require(self.media_review['output']['audio_policy']=='SILENT_CONTINUE','speech_review_audio_unavailable')

    def photo_work(self):
        return json.loads(c.canonical(dict(edits=self.edits,preview=self.preview,source_sha256=self.source_hashes,
            work_result=self.work_artifact.artifact_id,producer_count=self.producer_counts['photo_preview'])))

    def prepare_media(self):
        from . import media_continuation_v01 as continuation
        with self.lock:
            self.current()
            c.require('media' in self.contract and self.media_review is None and self.status=='ACTIVE','media_preparation_state')
            audio=next((s for s in self.services if s.role=='audio'),None)
            observed=dict(available=False,resource=None)
            if audio is not None:
                reply=audio.rpc('observe',{})
                c.require(reply['session']==self.id and reply['resource']==self.resource_plan['audio'],'actual_audio_observation')
                observed=dict(available=reply['available'],resource=reply['resource'])
            material=dict(contract=self.contract,media=self.media_fixture['manifest'],photo_work=self.photo_work(),audio_source=observed)
            self.media_review=continuation.assemble(self,material)
            self.producer_counts['media_contract']+=1
            c.require(self.media_review['output']['photo_work_ref']==c.identity('retained_photo',self.photo_work()),'D_photo_material_consumed')
            self.media_state.update(status='READY',audio='AVAILABLE' if observed['available'] else 'NOT_REQUESTED')
            authorization,inputs,observation,review=kernel.prepare_command(self,dict(op='SEEK',value=7),
                dict(actual_D_review=True,actual_media_output=self.media_review['output']['duration_seconds']==8))
            clock=self.source.sample(observation)
            packet,revision=hosts.install_current_action_v01(self.host,**authorization,inputs=inputs,
                admission_id=self.catalogue[2].admission_id,expected_revision=self.host.revision,evaluation_time=clock.evaluation_time,
                evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
            self.media_pending=dict(authorization=authorization,inputs=inputs,observation=observation,review=review,
                packet_id=packet,fact=self.last_prepared_fact,registry=self.host.registry)
            self.media_baseline=continuation.prepare_delta_baseline(self)
            return dict(result_id=self.media_review['results'][0].result.result_id,D_report=self.media_review['report'].validation_report_id
                if hasattr(self.media_review['report'],'validation_report_id') else self.media_review['bundle'].runtime_report.report_id)

    def withdraw_audio(self):
        """Initial resource-owner cleanup closes a real sink; E carries no effect handle."""
        from . import media_continuation_v01 as continuation
        with self.lock:
            self.current()
            c.require(self.media_review is not None and self.audio_loss is None,'audio_withdrawal_state')
            audio=next(s for s in self.services if s.role=='audio')
            self._observe_audio_liveness('LOSS_CONTINUATION')
            self.media_stop.set()
            if self.media_thread is not None:
                self.media_thread.join(timeout=12)
                c.require(not self.media_thread.is_alive(),'media_withdrawal_boundary')
            receipt=audio.close()
            c.require(receipt['reaped'] and audio.process.poll() is not None,'audio_actual_loss_required')
            self.media_state.update(audio='UNAVAILABLE',status='AUDIO_UNAVAILABLE_PAUSED')
            try:
                clock=self.source.sample()
                self.audio_loss=dict(receipt=receipt,cause=self.audio_fault or dict(kind='OWNER_WITHDRAWAL'),observed_at=clock.evaluation_time,event_ref=c.identity('audio_loss',
                    dict(session=self.id,resource=audio.nonce,receipt=receipt,now=clock.evaluation_time)),
                    prior_frames=self.media_state['frames'],prior_samples=self.media_state['samples'])
                pending=self.media_pending;prior=pending['observation']
                self.loss_dependency=self.media_dependency()
                self.loss_photo_work=self.photo_work()
                fact=dict(pending['fact'],media=self.loss_dependency)
                new_sha=c.digest(fact)
                # New source evidence has its own acquisition interval; old Root authority is immutable.
                observed_from=clock.evaluation_time
                observed_to=min(observed_from+120,self.expires)
                c.require(observed_from<observed_to,'workspace_expired')
                new_envelope=action.build_action_dependency_time_envelope_id_v01(dependency_id=prior.dependency_id,evidence_ref=prior.evidence_ref,
                    content_sha256=new_sha,freshness_policy_id=prior.freshness_policy_id,source_provenance_refs=prior.source_provenance_refs,
                    valid_from_utc=observed_from,valid_to_utc=observed_to)
                observation=action.build_action_dependency_current_observation_v01(dependency_id=prior.dependency_id,evidence_ref=prior.evidence_ref,
                    observed_content_sha256=new_sha,time_envelope_id=new_envelope,freshness_policy_id=prior.freshness_policy_id,
                    source_provenance_refs=prior.source_provenance_refs,valid_from_utc=observed_from,valid_to_utc=observed_to,
                    observed_at_utc=clock.evaluation_time,observation_context_id=clock.evaluation_context_id)
                clock=self.source.sample(observation)
                capture=hosts.capture_current_action_source_v01(self.host,packet_id=pending['packet_id'],expected_revision=self.host.revision,
                    evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
                self.audio_capture=capture
                invalidation=action.build_action_invalidation_evidence_v01(source_invalidation_event_ref=self.audio_loss['event_ref'],
                    packet_id=pending['packet_id'],dependency_id=prior.dependency_id,invalidation_class='DEPENDENCY_CHANGED',
                    evidence_ref=prior.evidence_ref,evidence_sha256=observation.observed_content_sha256,observed_status='CHANGED',
                    time_envelope_id=prior.time_envelope_id,freshness_policy_id=prior.freshness_policy_id,owning_local_root_id=self.root,
                    accepted_by_local_root_id=self.root,authority_effect='DETERMINISTIC_BLOCK',evaluation_time=capture.evaluation_time,
                    evaluation_time_source=capture.evaluation_time_source,evaluation_context_id=capture.evaluation_context_id)
                self.audio_invalidation=invalidation
                self.journal('AUDIO_ACTUAL_LOSS',event_ref=self.audio_loss['event_ref'],source_revision=capture.source_revision,
                    capture_ordinal=capture.capture_ordinal)
                before_effects=len(self.executed)
                try:
                    hosts.dispatch_current_action_v01(self.host,packet_id=pending['packet_id'],task_id=self.id,expected_revision=self.host.revision,
                        evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
                except ValueError as exc:
                    c.require(str(exc)=='host_current_action_not_executable','stale_audio_wrong_refusal:'+str(exc))
                    self.audio_loss['stale_packet_refusal']=str(exc)
                else:
                    raise ValueError('stale_audio_packet_executed')
                c.require(len(self.executed)==before_effects,'audio_loss_unexpected_effect')
                # The refused prestart checks advance the host; acquire a fresh public capture.
                capture=hosts.capture_current_action_source_v01(self.host,packet_id=pending['packet_id'],expected_revision=self.host.revision,
                    evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
                self.audio_capture=capture
                self.media_state.update(status='RECOMPUTING')
                self.media_delta=continuation.recompute(self,capture,invalidation,self.audio_loss['observed_at'])
                self.producer_counts['delta']+=1
                self.audio_fault=None
                # Completed common work is activity, not a renewed session lifetime.
                self.last_activity=time.monotonic()
                self.media_state.update(status='SILENT_READY' if self.media_delta['consumed']['audio_policy']=='SILENT_CONTINUE' else 'AUDIO_REQUIRED_PAUSED',
                    continuation_ref=self.media_delta['consumed']['delta_result_ref'])
                self.pending=None
                return self.state()
            except BaseException as exc:
                error=dict(type=type(exc).__name__,reason=str(exc))
                if self.audio_loss is not None:
                    self.audio_loss['continuation_error']=error
                self.media_state.update(audio='UNAVAILABLE',status='AUDIO_UNAVAILABLE_PAUSED',
                    reason=error['type']+':'+error['reason'])
                raise

    def execute_media(self,op,value,invocation_id,expires):
        from .media_v01 import preview_dimensions
        import wave
        c.require(self.media_review is not None,'media_requires_actual_D_review')
        plan=self.media_review['output']
        if op in ('PLAY','REVIEW_MEDIA'):
            self._check_audio_current('EXECUTOR')
        if op=='REVIEW_MEDIA':
            if plan['speech_review']:
                c.require(self.audio_loss is None and self.media_state['samples']>0,'speech_review_audio_unavailable')
                self.media_state['review']='AWAITING_HUMAN_SPEECH_ASSESSMENT_NO_AUTOMATIC_INTELLIGIBILITY_CLAIM'
            else:
                c.require(self.media_state['frames']>0,'media_review_needs_frames')
                self.media_state['review']='VISUAL_MATERIAL_PRESENTED'
            return
        self.media_stop.set()
        if self.media_thread is not None:
            self.media_thread.join(timeout=12)
            c.require(not self.media_thread.is_alive(),'prior_media_batch_not_stopped')
        audio=next((s for s in self.services if s.role=='audio' and s.process.poll() is None),None)
        if audio is not None:audio.rpc('end',{})
        if op in ('PAUSE','SEEK'):
            if op=='SEEK':self.media_state['position']=value
            self.media_state['status']='PAUSED'
            return
        c.require(self.audio_loss is None or self.media_delta is not None,'audio_loss_requires_current_E')
        c.require(self.audio_loss is None or plan['audio_policy']=='SILENT_CONTINUE','speech_review_audio_unavailable')
        frames=[p.read_bytes() for p in self.media_fixture['frames']]
        c.require([c.digest(b) for b in frames]==plan['frame_sha256s'],'media_frame_sources_changed')
        c.require(all(preview_dimensions(b)==(480,270) for b in frames),'media_frame_format')
        with wave.open(str(self.media_fixture['audio']),'rb') as stream:pcm=stream.readframes(64000)
        c.require(c.digest(pcm)==plan['pcm_sha256'],'media_pcm_source_changed')
        stop=threading.Event();self.media_stop=stop
        offset=int(self.media_state['position']*plan['fps'])%len(frames)
        batch=c.identity('media_batch',dict(session=self.id,invocation=invocation_id,plan=plan,offset=offset,
            delta=None if self.media_delta is None else self.media_delta['consumed']))
        audio=next((s for s in self.services if s.role=='audio' and s.process.poll() is None),None)
        display=next(s for s in self.services if s.role=='display')
        deadline=min(self.deadline,time.monotonic()+max(0,expires-self.source.sample().evaluation_time))
        if audio is not None:
            audio.rpc('begin',dict(batch_ref=batch,sample_offset=offset*4000,deadline=min(deadline,time.monotonic()+9)))
        self.media_state['status']='PLAYING'
        def play():
            try:
                for i in range(offset,len(frames)):
                    if stop.is_set() or self.revoked or time.monotonic()>=deadline:break
                    self._check_audio_current('FINITE_DELIVERY')
                    frame_ref=c.identity('media_frame',dict(batch=batch,index=i,sha256=c.digest(frames[i])))
                    args=dict(png=base64.b64encode(frames[i]).decode(),sha256=c.digest(frames[i]),frame_ref=frame_ref.replace('ews:media_frame:','ews:frame:'))
                    if self.contract['minimize']=='preview_only':
                        args['derived']=dict(width=480,height=270,exposure=0,crop='ORIGINAL',preview=self.contract['preview'])
                    delivered=display.rpc('put',args)
                    c.require(delivered['sha256']==args['sha256'] and delivered['frame_ref']==args['frame_ref'],'media_display_output_binding')
                    received=None
                    if audio is not None and self.audio_loss is None:
                        chunk=pcm[i*8000:(i+1)*8000]
                        received=audio.rpc('consume',dict(pcm=base64.b64encode(chunk).decode(),sha256=c.digest(chunk),
                            sample_offset=i*4000,frame_ref=frame_ref,batch_ref=batch))
                        c.require(received['sha256']==c.digest(chunk) and received['sample_offset']==i*4000 and
                            received['resource']==audio.nonce and received['session']==self.id and received['batch_ref']==batch,
                            'audio_actual_output_binding')
                        c.exact(received,('session','resource','samples','sample_offset','sha256','peak','frame_ref','batch_ref'))
                        c.require(received['samples']==4000 and received['frame_ref']==frame_ref,'audio_frame_sample_binding')
                        self.media_state['samples']+=received['samples']
                    self.media_snapshot=(args['frame_ref'],args['sha256'],frames[i])
                    self.media_state.update(position=(i+1)/plan['fps'],frames=self.media_state['frames']+1,
                        frame_ref=args['frame_ref'],frame_sha256=args['sha256'])
                    self.media_events.append(dict(batch=batch,index=i,frame_sha256=args['sha256'],audio=received,
                        current_monotonic=time.monotonic(),native_invocation=invocation_id))
                    if stop.wait(1/plan['fps']):break
                self.media_state['status']='PAUSED' if stop.is_set() else 'FINISHED'
            except BaseException as exc:
                self._observe_audio_liveness('DELIVERY_EXCEPTION')
                self.media_state.update(status='AUDIO_UNAVAILABLE_PAUSED' if self.audio_fault else 'FAILED',reason=type(exc).__name__+':'+str(exc))
        self.media_thread=threading.Thread(target=play,name='ews-finite-media',daemon=False)
        self.media_thread.start()

    def revoke(self):
        with self.lock:
            self.current()
            evidence=c.identity('withdrawal',dict(session=self.id,version=self.version,owner='ews:owner'))
            decision=kernel.root_review(self.root,'transaction:'+self.id,evidence,self.id,
                dict(owning_root=self.host.owning_root_id==self.root,active_workspace=self.status=='ACTIVE'),
                evidence,self.program.candidate.bsep_ref,self.program.topology_artifact.artifact_id,
                self.source.sample().evaluation_time,predicate='workspace_owner_withdrawal',kind='WORKSPACE_WITHDRAWAL')
            self.revoked=decision[2].decision=='ACCEPT'
            self.withdrawal=kernel.roots.root_decision_result_to_plain_dict_v01(decision[2])
            return self.close('ROOT_ACCEPTED_WORKSPACE_WITHDRAWAL')

    def poll_lifetime(self):
        if time.monotonic()>=self.deadline:
            self.close('TTL_EXPIRED')
        elif self.contract['cleanup']=='on_end_and_idle' and time.monotonic()-self.last_activity>=300:
            self.close('IDLE_EXPIRED')

    def report(self):
        return dict(version=c.VERSION,state=self.state(),contract=self.contract,mode=self.mode,
            work_topology=abi.kernel_artifact_to_plain_dict_v01(self.program.topology_artifact),
            work_result=abi.kernel_artifact_to_plain_dict_v01(self.work_artifact),
            root_route_decision=kernel.roots.root_decision_result_to_plain_dict_v01(self.route_review[2]),
            commands=self.history,timings=self.timings,cleanup=self.cleanup_report,
            withdrawal=getattr(self,'withdrawal',None),
            memory_origin=getattr(self,'memory_origin',None),audio_fault=self.audio_fault,
            source_preserved=all(c.digest(p.read_bytes())==self.source_hashes[n] for n,p in self.assets.items()),
            source_hashes=self.source_hashes,resource_plan=self.resource_plan,write_outcome=self.write_outcome,
            privacy_consumption=dict(minimize=self.contract['minimize'],transfers=self.privacy_transfers,
                boundary='derived pixels only; optional safe derived dimensions/transforms in preview_only'),
            service_ipc=[dict(role=s.role,birth=s.birth,events=s.events) for s in self.services],
            external_device_business_effects=0,full_fractal_execution='CONSUMED_BY_WORK' if self.media_review else 'NOT_RUN',
            delta_audio_loss='CONSUMED' if self.media_delta else 'NOT_COMPLETED' if self.audio_loss else 'NOT_RUN',
            semantic_drs='ACTUAL_CURRENT_CANDIDATE_DESCENT' if getattr(self,'memory_origin',None) else 'NO_MEMORY_INPUT',
            media_fixture=None if self.media_fixture is None else self.media_fixture['manifest'],
            media_state=dict(self.media_state),audio_loss=self.audio_loss,producer_counts=dict(self.producer_counts),
            media_events=list(self.media_events),
            media_consumption=None if self.media_delta is None else self.media_delta['consumed'],
            media_sources_preserved=self.media_fixture is None or (
                [c.digest(p.read_bytes()) for p in self.media_fixture['frames']]==[v['sha256'] for v in self.media_fixture['manifest']['frames']] and
                c.digest(self.media_fixture['audio'].read_bytes())==self.media_fixture['manifest']['audio']['sha256']),
            operation_scope='finite frame sequence and headless PCM consumption; no physical sound or speech intelligibility claim')
