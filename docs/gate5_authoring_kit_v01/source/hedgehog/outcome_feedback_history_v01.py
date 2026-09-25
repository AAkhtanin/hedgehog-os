"""Single-writer local genesis, exact new Root review, and semantic discovery.

Independent native proof/context are application inputs, never fields recovered
from a candidate report. The G32 genesis service remains unchanged; the separate
G34 service adds finite history epochs and current advisory consumption.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time

from hedgehog import outcome_feedback_v01 as g3
from hedgehog.drs import LocalDRS
from hedgehog.local_drs_resolver import SemanticDRSRecordInput, SemanticResolveQuery, write_semantic_record, resolve_semantic_candidates
from hedgehog.kernel import abi_v01 as abi, work_composition_v01 as work, semantic_work_v01 as semantic, root_decision_v01 as roots, trust_model_v01 as trust
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01

PURPOSE='RECORD_VERIFIED_OUTCOME_GENESIS_ONLY'
POLICY='g32:root_reviewed_local_genesis:v01'


HISTORY_PROFILE_G34 = 'G34_DURABLE_SOURCE_BOUND_HISTORY_V01'


def validate_history_delivery_refs_v01(event_refs,independent_refs):
    """Pure source-membership predicate shared by actual admission and replay."""
    from .outcome_feedback_consumer_v01 import require
    require(type(event_refs) in (list,tuple) and 0<len(event_refs)<=256,'g34_delivery_bound')
    require(all(ref in independent_refs for ref in event_refs),'g34_missing_independent_source')


def validate_history_root_context_v01(history_key,root):
    """Pure request identity check; this grants no descent or Root authority."""
    from .outcome_feedback_consumer_v01 import require
    require(history_key['local_root_scope_id']==root,'g34_current_root_key')


@dataclass(frozen=True, slots=True)
class HistorySnapshotV01:
    canonical: bytes

    def to_plain_data(self):
        from .outcome_feedback_consumer_v01 import require, identity
        from . import outcome_calibration_v01 as cal
        require(type(self.canonical) is bytes and len(self.canonical)<=524288,'g34_snapshot_bound')
        value=json.loads(self.canonical)
        require(len(self.canonical)<=524288 and canonical_json_bytes_v01(value)==self.canonical,'g34_snapshot_bound')
        require(set(value)=={'snapshot_id','profile','epoch','predecessor','event_refs','source_pins','fold','updates',
            'prior','evaluated_at','valid_from','valid_to','corrections'}|({'review_source_projections'} if 'review_source_projections' in value else set()),'g34_snapshot_shape')
        if 'review_source_projections' in value:
            rows=value['review_source_projections']
            require(type(rows) is list and len(rows)==len(value['event_refs']) and
                [r['event_ref'] for r in rows]==value['event_refs'] and
                all(r['source_sha256']==value['source_pins'][r['event_ref']] for r in rows),'g36r_snapshot_review_sources')
        require(value['profile']==HISTORY_PROFILE_G34 and type(value['epoch']) is int and 0<=value['epoch']<=256,'g34_snapshot_profile')
        require(all(type(value[n]) is int and 0<=value[n]<=253402300799 for n in ('evaluated_at','valid_from','valid_to'))
            and value['valid_from']<=value['evaluated_at']<value['valid_to']
            and 0<value['valid_to']-value['valid_from']<=604800,'g34_snapshot_time')
        require(type(value['event_refs']) is list and 0<len(value['event_refs'])<=256
            and all(type(ref) is str and len(ref)==64 for ref in value['event_refs']),'g34_snapshot_events')
        require(type(value['source_pins']) is dict and set(value['source_pins'])==set(value['event_refs'])
            and all(type(v) is str and len(v)==64 for v in value['source_pins'].values()),'g34_snapshot_sources')
        require(type(value['updates']) is list and len(value['updates'])<=64,'g34_snapshot_updates')
        updates=tuple(cal.GTTrustUpdateV01(canonical_json_bytes_v01(v)) for v in value['updates'])
        cal.GTEventFoldV01(canonical_json_bytes_v01(value['fold']),updates)
        cal.AVFHistoryPriorV01(canonical_json_bytes_v01(value['prior']))
        require(type(value['corrections']) is list and len(value['corrections'])<=64,'g34_snapshot_corrections')
        require(value['snapshot_id']==identity('snapshot',{k:v for k,v in value.items() if k!='snapshot_id'}),'g34_snapshot_identity')
        return value


def _history_pointer_v01(key,fields):
    """Keep accepted references; encode a generated digest if DRS rejects it."""
    from hedgehog import drs_semantic_address_v01 as address
    from .outcome_feedback_consumer_v01 import require
    require(type(key) is str and len(key)==64 and all(c in '0123456789abcdef' for c in key),'g34_snapshot_reference')
    try:return address.build_artifact_pointer_v01(object_reference='g34:payload:'+key,**fields)
    except ValueError as error:
        if str(error)!='drs_secret_payload_forbidden':raise
    # A digest can contain 13-19 consecutive digits. This reversible alphabet
    # represents that same generated identity without resembling a card number.
    encoded=''.join('abcdefghijklmnop'[int(c,16)] for c in key)
    return address.build_artifact_pointer_v01(object_reference='g34:payload:hexletters:'+encoded,**fields)


def _history_payload_pointer_v01(value):
    return _history_pointer_v01(value['snapshot_id'],dict(storage_class='LOCAL_DOCUMENT',
        content_sha256=hashlib.sha256(canonical_json_bytes_v01(value)).hexdigest(),media_type='application/json',
        byte_length=len(canonical_json_bytes_v01(value)),access_policy_id='g34:history_context_read:v01',
        sensitivity_class='INTERNAL',allowed_use_classes=('OPEN_ONE_ARTIFACT',),forbidden_use_classes=(),
        summary_read_permitted=True,payload_read_permitted=True))


class OutcomeHistoryV01:
    """Finite single-writer history. Trusted source anchors are independent inputs.

    A fetched record never supplies its own trusted source map. Immutable epochs
    are installed before atomic head publication under a local exclusive lock.
    """
    def __init__(self, directory, *, trusted_events, trusted_corrections=()):
        from . import outcome_calibration_v01 as cal
        from .outcome_feedback_consumer_v01 import require
        self.directory=Path(directory)
        self.directory.mkdir(parents=True,exist_ok=True)
        self.sources={}
        self._opened={}
        self.read_audit=[]
        self.corrections={}
        for event in trusted_events:
            require(type(event) is cal.SourceBoundGTEventV01 and event.source_profile_id in (g3.PREDICTIVE_SOURCE_PROFILE_ID,g3.ACTION_ADVICE_SOURCE_PROFILE_ID),'g34_native_history_only')
            key=json.loads(event.feedback_canonical)['feedback_id']
            old=self.sources.get(key)
            require(old is None or old==event,'g34_source_anchor_conflict')
            self.sources[key]=event
        for instruction in trusted_corrections:
            require(type(instruction) is bytes,'g34_independent_correction_bytes')
            value=json.loads(instruction)
            self._validate_correction_instruction(value)
            self.corrections[value['instruction_id']]=instruction
        self.drs=LocalDRS(self.directory/'drs')

    def head_v01(self):
        from .outcome_feedback_consumer_v01 import require
        path=self.directory/'HEAD.json'
        if not path.exists(): return None
        require(path.is_file() and not path.is_symlink(),'g34_head_shape')
        head=json.loads(path.read_bytes())
        self._head_shape(head)
        return head

    @staticmethod
    def _head_shape(head):
        from .outcome_feedback_consumer_v01 import require
        require(type(head) is dict,'g34_head_shape')
        require(set(head)=={'snapshot_id','body_sha256','record_id','descriptor_sha256'},'g34_head_shape')
        require(type(head['record_id']) is str and 0<len(head['record_id'])<=4096,'g34_head_fields')
        require(all(type(head[k]) is str and len(head[k])==64 and all(c in '0123456789abcdef' for c in head[k])
            for k in ('snapshot_id','body_sha256','descriptor_sha256')),'g34_head_fields')

    def _validate_correction_instruction(self,value):
        from .outcome_feedback_consumer_v01 import require, identity
        require(type(value) is dict and set(value)=={'instruction_id','profile','old_event','new_event','old_source_sha256',
            'new_source_sha256','old_occurrence','new_occurrence','old_claim','new_claim','root','history_key','subject',
            'predecessor','reason','scope'},'g34_correction_instruction_shape')
        require(value['profile']=='G34_CONTROLLED_HISTORY_OWNER_REPLACEMENT_V01'
            and value['scope']=='ONE_DECLARED_CONTROLLED_COMPARISON_NOT_MEASUREMENT_CORRECTION'
            and type(value['reason']) is str and 0<len(value['reason'])<=256,'g34_correction_instruction_scope')
        require(value['instruction_id']==identity('owner_correction',{k:v for k,v in value.items() if k!='instruction_id'}),'g34_correction_instruction_id')
        for side in ('old','new'):
            event=self.sources.get(value[side+'_event']);require(event is not None,'g34_correction_instruction_source')
            f=json.loads(event.feedback_canonical)
            require(value[side+'_source_sha256']==hashlib.sha256(event.source_canonical).hexdigest()
                and value[side+'_occurrence']==f['observation_id'] and value[side+'_claim']==f['gt_advice_ref']
                and value['root']==f['local_root_scope_id'] and value['history_key']==f['avf_history_key']
                and value['subject']==f['advisory_subject_key'],'g34_correction_instruction_binding')

    def _correction(self,previous,replacement,reason,head):
        from .outcome_feedback_consumer_v01 import require
        matches=[]
        for raw in self.corrections.values():
            value=json.loads(raw);self._validate_correction_instruction(value)
            if (value['old_event'],value['new_event'],value['reason'],value['predecessor'])==(previous,replacement,reason,head):matches.append(value)
        require(len(matches)==1,'g34_independent_correction_required')
        return matches[0]['instruction_id']

    def _derive(self,event_refs,*,epoch,predecessor,evaluated_at,corrections):
        from . import outcome_calibration_v01 as cal
        from .outcome_feedback_consumer_v01 import require, identity
        validate_history_delivery_refs_v01(event_refs,self.sources)
        events=tuple(self.sources[ref] for ref in event_refs)
        require(all(json.loads(e.feedback_canonical)['timestamp']<=evaluated_at for e in events),'g34_write_before_arrival')
        fold=cal.bounded_gt_event_fold_v01(events,evaluated_at=evaluated_at)
        prior=cal.fold_avf_history_prior_v01(events,evaluated_at=evaluated_at)
        windows=[g3._source(cal._source_bundle(e),e.source_profile_id)[0]['native']['time_envelope'] for e in events]
        valid_from=max(cal._iso_epoch(w['valid_from']) for w in windows)
        valid_to=min(cal._iso_epoch(w['valid_to']) for w in windows)
        require(valid_from<=evaluated_at<valid_to,'g34_history_write_time')
        material=dict(profile=HISTORY_PROFILE_G34,epoch=epoch,predecessor=predecessor,event_refs=list(event_refs),
            source_pins={ref:hashlib.sha256(self.sources[ref].source_canonical).hexdigest() for ref in sorted(set(event_refs))},
            fold=fold.to_plain_data(),updates=[v.to_plain_data() for v in fold.updates],prior=prior.to_plain_data(),
            evaluated_at=evaluated_at,valid_from=valid_from,valid_to=valid_to,corrections=corrections)
        from .domains.supplier_water_filter import adversarial_feedback_v01 as supplier
        if all(e.source_profile_id==supplier.PROFILE and json.loads(e.source_canonical).get('collector')==supplier.COLLECTOR for e in events):
            material['review_source_projections']=[supplier.provenance_row_v01(supplier.ActionAdviceSourceContextV01(e.source_canonical),e) for e in events]
        material['snapshot_id']=identity('snapshot',material)
        result=HistorySnapshotV01(canonical_json_bytes_v01(material));result.to_plain_data()
        return result

    def prepare_v01(self,event_refs,*,expected_head,evaluated_at,corrections=()):
        from .outcome_feedback_consumer_v01 import require, ordinary_review_v01, review_to_plain_v01
        require(self.head_v01()==expected_head,'g34_stale_predecessor')
        old=self.read_v01(expected_head['snapshot_id']) if expected_head else None
        refs=list(old['snapshot']['event_refs']) if old else []
        correction_rows=[]
        for previous,replacement,reason in corrections:
            relation=self._correction(previous,replacement,reason,expected_head)
            require(previous in refs and replacement in event_refs and previous!=replacement
                and type(reason) is str and bool(reason),'g34_correction_provenance')
            require(previous in self.sources and replacement in self.sources,'g34_correction_source')
            a=json.loads(self.sources[previous].feedback_canonical);b=json.loads(self.sources[replacement].feedback_canonical)
            require(a['avf_history_key']==b['avf_history_key'] and a['observation_id']!=b['observation_id']
                and self.sources[previous].source_canonical!=self.sources[replacement].source_canonical,'g34_correction_source')
            refs=[ref for ref in refs if ref!=previous]
            correction_rows.append(dict(replaces=previous,replacement=replacement,reason=reason,instruction_id=relation))
        # Redelivery is retained in GT's delivery audit; it does not become a sample.
        refs.extend(event_refs)
        snapshot=self._derive(refs,epoch=old['snapshot']['epoch']+1 if old else 0,
            predecessor=expected_head,evaluated_at=evaluated_at,corrections=correction_rows)
        value=snapshot.to_plain_data();root=value['prior']['history_key']['local_root_scope_id']
        proposal=dict(snapshot_id=value['snapshot_id'],expected_head=expected_head,source_pins=value['source_pins'],
            fold_id=value['fold']['fold_id'],prior_id=value['prior']['prior_id'],corrections=correction_rows,
            root=root,epoch=value['epoch'],evaluated_at=evaluated_at)
        review=ordinary_review_v01(root=root,transaction='g34:history:'+value['snapshot_id'],
            candidates={value['snapshot_id']:proposal},selected=value['snapshot_id'],scores={value['snapshot_id']:1000000},
            evidence_ref=value['snapshot_id'],now=evaluated_at,predicate='g34_record_exact_history')
        require(review[2].decision=='ACCEPT','g34_record_root_refusal')
        return snapshot,review

    def _review(self,value):
        from .outcome_feedback_consumer_v01 import ordinary_review_v01
        root=value['prior']['history_key']['local_root_scope_id'];key=value['snapshot_id']
        proposal=dict(snapshot_id=key,expected_head=value['predecessor'],source_pins=value['source_pins'],
            fold_id=value['fold']['fold_id'],prior_id=value['prior']['prior_id'],corrections=value['corrections'],
            root=root,epoch=value['epoch'],evaluated_at=value['evaluated_at'])
        return ordinary_review_v01(root=root,transaction='g34:history:'+key,candidates={key:proposal},
            selected=key,scores={key:1000000},evidence_ref=key,now=value['evaluated_at'],predicate='g34_record_exact_history')

    def _meaning(self,value,review):
        from hedgehog import drs_semantic_address_v01 as address
        from .outcome_feedback_consumer_v01 import identity
        key=value['prior']['history_key'];now=value['evaluated_at'];end=value['valid_to']
        addr=address.build_semantic_address_v01(namespace='g34',domain=key['domain_scope_id'],subject_class='source_bound_history',
            intent_class='context_lookup',meaning_schema_id=HISTORY_PROFILE_G34,meaning_schema_version='v01')
        env=address.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=value['fold']['history_observation_anchor'] or now,
            ct_context_anchor=now,ttl_seconds=end-now,valid_from=now,valid_to=end,source_observed_at=now,source_reported_at=now,
            system_ingested_at=now,system_verified_at=now,freshness_policy_id='g34:bounded_history')
        auth=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=key['local_root_scope_id'],
            source_root_decision_input_id=review[1].decision_input_id,source_root_decision_id=review[2].decision_id,
            source_root_decision_hash=hashlib.sha256(canonical_json_bytes_v01(roots.root_decision_result_to_plain_dict_v01(review[2]))).hexdigest(),
            authority_scope_fingerprint=identity('history_key',key),root_acceptance_state='ACCEPTED_WORK',recording_component='g34:history')
        return address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
            safe_summary=value['snapshot_id'],
            semantic_tags=('g34_history',),resonance_reason='Source-bound evidence only; current Root review is mandatory.',
            memory_pointers=(),artifact_pointers=(_history_payload_pointer_v01(value),),source_reference_ids=tuple(sorted(set(value['event_refs']))),lineage_edges=(),
            time_envelope=env,authority_envelope=auth,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),
            reuse_policy_class='CONTEXT_ONLY',policy_version=key['policy_semantics_version'],schema_versions=(HISTORY_PROFILE_G34,),
            content_fingerprint=identity('snapshot_body',value),recording_component='g34:history')

    def read_v01(self,snapshot_id,*,expected_sha256=None):
        from hedgehog import drs_semantic_address_v01 as address
        from .outcome_feedback_consumer_v01 import require, review_to_plain_v01
        require(type(snapshot_id) is str and len(snapshot_id)==64 and all(c in '0123456789abcdef' for c in snapshot_id),'g34_snapshot_reference')
        path=self.directory/'epochs'/(snapshot_id+'.json')
        require(path.is_file() and not path.is_symlink() and path.stat().st_mode & 0o777==0o644,'g34_epoch_body_mode')
        raw=path.read_bytes()
        require(expected_sha256 is None or hashlib.sha256(raw).hexdigest()==expected_sha256,'g34_epoch_hash')
        data=json.loads(raw);require(set(data)=={'snapshot','review','meaning'},'g34_epoch_shape')
        value=data['snapshot'];HistorySnapshotV01(canonical_json_bytes_v01(value)).to_plain_data()
        self._validate_ancestry(value)
        expected=self._derive(value['event_refs'],epoch=value['epoch'],predecessor=value['predecessor'],
            evaluated_at=value['evaluated_at'],corrections=value['corrections'])
        require(expected.canonical==canonical_json_bytes_v01(value) and value['snapshot_id']==snapshot_id,'g34_snapshot_source_mismatch')
        review=self._review(value)
        require(review_to_plain_v01(review)==data['review'],'g34_record_root_mismatch')
        require(address.meaning_record_to_plain_data_v01(self._meaning(value,review))==data['meaning'],'g34_meaning_mismatch')
        payload_path=self.directory/'epochs'/(snapshot_id+'.payload.json')
        require(payload_path.is_file() and not payload_path.is_symlink()
            and payload_path.read_bytes()==canonical_json_bytes_v01(value),'g34_epoch_payload_mismatch')
        descriptor=dict(snapshot_id=snapshot_id,history_key=value['prior']['history_key'],meaning=data['meaning'],
            root_review=data['review'],body_sha256=hashlib.sha256(raw).hexdigest(),prior_id=value['prior']['prior_id'])
        require((self.directory/'epochs'/(snapshot_id+'.descriptor.json')).read_bytes()==canonical_json_bytes_v01(descriptor),'g34_epoch_descriptor_mismatch')
        return data

    def _validate_ancestry(self,value):
        from collections import Counter
        from .outcome_feedback_consumer_v01 import require
        previous=value['predecessor']
        if previous is None:
            require(value['epoch']==0 and not value['corrections'],'g34_genesis_ancestry')
            return
        require(type(previous) is dict and set(previous)=={'snapshot_id','body_sha256','record_id','descriptor_sha256'},'g34_predecessor_shape')
        key=previous['snapshot_id']
        require(type(key) is str and len(key)==64 and all(c in '0123456789abcdef' for c in key),'g34_predecessor_reference')
        raw=(self.directory/'epochs'/(key+'.json')).read_bytes()
        require(hashlib.sha256(raw).hexdigest()==previous['body_sha256'],'g34_predecessor_hash')
        prior=json.loads(raw)['snapshot']
        require(type(prior['epoch']) is int and value['epoch']==prior['epoch']+1,'g34_epoch_sequence')
        old=self.read_v01(key,expected_sha256=previous['body_sha256'])
        require(old['meaning']['meaning_record_id']==previous['record_id'] and prior['prior']['history_key']==value['prior']['history_key']
            and value['evaluated_at']>=prior['evaluated_at'],'g34_predecessor_context')
        refs=list(prior['event_refs']);seen=set()
        for correction in value['corrections']:
            require(type(correction) is dict and set(correction)=={'replaces','replacement','reason','instruction_id'},'g34_correction_shape')
            before,after=correction['replaces'],correction['replacement']
            require(correction['instruction_id']==self._correction(before,after,correction['reason'],previous),'g34_correction_relation_changed')
            require(before in refs and before not in seen and after in value['event_refs'] and before!=after
                and type(correction['reason']) is str and 0<len(correction['reason'])<=256,'g34_correction_provenance')
            require(before in self.sources and after in self.sources and self.sources[before].source_canonical!=self.sources[after].source_canonical,
                'g34_correction_source')
            a=json.loads(self.sources[before].feedback_canonical);b=json.loads(self.sources[after].feedback_canonical)
            require(a['avf_history_key']==b['avf_history_key'] and a['observation_id']!=b['observation_id'],'g34_correction_source')
            refs=[ref for ref in refs if ref!=before];seen.add(before)
        require(Counter(refs)<=Counter(value['event_refs']),'g34_unauthorized_history_removal')

    def commit_v01(self,snapshot,review,*,expected_head):
        import fcntl, os
        from hedgehog import drs_semantic_address_v01 as address
        from .outcome_feedback_consumer_v01 import require, review_to_plain_v01
        value=snapshot.to_plain_data()
        self._validate_ancestry(value)
        require(value['predecessor']==expected_head,'g34_expected_predecessor')
        expected=self._derive(value['event_refs'],epoch=value['epoch'],predecessor=expected_head,
            evaluated_at=value['evaluated_at'],corrections=value['corrections'])
        require(expected.canonical==snapshot.canonical,'g34_snapshot_source_mismatch')
        require(review_to_plain_v01(review)==review_to_plain_v01(self._review(value)),'g34_write_review_substitution')
        with (self.directory/'writer.lock').open('a+b') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            try:
                require(self.head_v01()==expected_head,'g34_stale_predecessor')
                meaning=self._meaning(value,review)
                body=canonical_json_bytes_v01(dict(snapshot=value,review=review_to_plain_v01(review),
                    meaning=address.meaning_record_to_plain_data_v01(meaning)))
                epochs=self.directory/'epochs';epochs.mkdir(exist_ok=True)
                destination=epochs/(value['snapshot_id']+'.json')
                installed=False;record_path=None
                try:
                    if destination.exists(): require(destination.read_bytes()==body,'g34_epoch_collision')
                    else:
                        with destination.open('xb') as stream: stream.write(body);stream.flush();os.fsync(stream.fileno())
                        destination.chmod(0o644);installed=True
                    now=value['evaluated_at'];end=value['valid_to'];key=value['prior']['history_key']
                    record=write_semantic_record(self.drs,SemanticDRSRecordInput(record_id=meaning.meaning_record_id,
                        domain=key['domain_scope_id'],content=dict(kind=HISTORY_PROFILE_G34,history_key=key,
                            snapshot_id=value['snapshot_id'],record=address.meaning_record_to_plain_data_v01(meaning)),
                        semantic_keys=('g34_history',),time_envelope=dict(pt_created_at=g3._utc(now),kt_asof=g3._utc(now),
                            et_observed_at=g3._utc(now),ct_session_anchor=value['snapshot_id'],ttl_seconds=end-now,
                            freshness_class='static',valid_from=g3._utc(now),valid_to=g3._utc(end)),
                        provenance=dict(request_id=value['snapshot_id'],created_by='root_orchestrator',trace_refs=[dict(trace_id=value['snapshot_id'])]),
                        root_final_ref=review[2].decision_id,worldstate_ref=value['prior']['prior_id']))
                    record_path=self.directory/'drs'/'work'/(record['record_id']+'.json')
                    def install_immutable(path,raw):
                        if path.exists():require(not path.is_symlink() and path.read_bytes()==raw,'g34_immutable_body_collision')
                        else:
                            with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
                            path.chmod(0o644)
                    payload_path=epochs/(value['snapshot_id']+'.payload.json')
                    install_immutable(payload_path,snapshot.canonical)
                    descriptor=dict(snapshot_id=value['snapshot_id'],history_key=key,meaning=address.meaning_record_to_plain_data_v01(meaning),
                        root_review=review_to_plain_v01(review),body_sha256=hashlib.sha256(body).hexdigest(),prior_id=value['prior']['prior_id'])
                    descriptor_raw=canonical_json_bytes_v01(descriptor)
                    install_immutable(epochs/(value['snapshot_id']+'.descriptor.json'),descriptor_raw)
                    head=dict(snapshot_id=value['snapshot_id'],body_sha256=hashlib.sha256(body).hexdigest(),record_id=meaning.meaning_record_id,
                        descriptor_sha256=hashlib.sha256(descriptor_raw).hexdigest())
                    tmp=self.directory/'HEAD.pending'
                    with tmp.open('xb') as stream: stream.write(canonical_json_bytes_v01(head));stream.flush();os.fsync(stream.fileno())
                    os.replace(tmp,self.directory/'HEAD.json')
                except BaseException:
                    (self.directory/'HEAD.pending').unlink(missing_ok=True)
                    if installed: destination.unlink(missing_ok=True)
                    if installed:
                        (epochs/(value['snapshot_id']+'.payload.json')).unlink(missing_ok=True)
                        (epochs/(value['snapshot_id']+'.descriptor.json')).unlink(missing_ok=True)
                    if record_path is not None: record_path.unlink(missing_ok=True)
                    raise
                require(self.head_v01()==head,'g34_readback')
                self.read_v01(value['snapshot_id'],expected_sha256=head['body_sha256'])
                return head
            finally: fcntl.flock(lock,fcntl.LOCK_UN)

    def _descriptor(self,head):
        from dataclasses import fields
        from hedgehog import drs_semantic_address_v01 as address
        from .outcome_feedback_consumer_v01 import require
        self._head_shape(head)
        path=self.directory/'epochs'/(head['snapshot_id']+'.descriptor.json')
        require(path.is_file() and not path.is_symlink() and path.stat().st_size<=65536,'g34_descriptor_bound')
        raw=path.read_bytes();require(hashlib.sha256(raw).hexdigest()==head['descriptor_sha256'],'g34_descriptor_hash')
        data=json.loads(raw)
        require(set(data)=={'snapshot_id','history_key','meaning','root_review','body_sha256','prior_id'}
            and data['snapshot_id']==head['snapshot_id'] and data['body_sha256']==head['body_sha256'],'g34_descriptor_binding')
        def record(cls,v):
            require(set(v)=={f.name for f in fields(cls)},'g34_descriptor_shape')
            return cls(**{k:tuple(x) if type(x) is list else x for k,x in v.items()})
        m=dict(data['meaning'])
        for name,cls in (('semantic_address',address.SemanticAddressV01),('time_envelope',address.DRSTimeEnvelopeV01),
                         ('authority_envelope',address.DRSAuthorityEnvelopeV01)):
            m[name]=record(cls,m[name])
        m['artifact_pointers']=tuple(record(address.ArtifactPointerV01,p) for p in m['artifact_pointers'])
        require(not m['memory_pointers'] and not m['lineage_edges'],'g34_descriptor_finite')
        meaning=record(address.MeaningRecordV01,m)
        require(address.validate_meaning_record_v01(meaning)[0] and meaning.meaning_record_id==head['record_id'],'g34_descriptor_meaning')
        self.read_audit.append(dict(stage='DESCRIPTOR',snapshot=head['snapshot_id']))
        return data,meaning

    def current_descriptor_v01(self,head,*,history_key):
        """Bounded eligibility input. This method never reads numerical payloads."""
        from .outcome_feedback_consumer_v01 import require
        data,meaning=self._descriptor(head)
        require(data['history_key']==history_key,'g34_current_key')
        require(len(meaning.artifact_pointers)==1,'g34_payload_pointer_required')
        pointer=meaning.artifact_pointers[0]
        require(pointer.access_policy_id=='g34:history_context_read:v01' and pointer.byte_length is not None
            and 0<pointer.byte_length<=524288 and pointer==_history_pointer_v01(head['snapshot_id'],
                {k:getattr(pointer,k) for k in ('storage_class','content_sha256','media_type','byte_length','access_policy_id',
                    'sensitivity_class','allowed_use_classes','forbidden_use_classes','summary_read_permitted','payload_read_permitted')}),'g34_payload_pointer_scope')
        return data,meaning

    def current_v01(self,*,history_key,root,transaction,evaluation_time):
        """Discover, qualify, rank, Root-approve and open before projecting history."""
        from dataclasses import asdict
        from hedgehog import drs_memory_resolution_v01 as memory, drs_semantic_address_v01 as address
        from . import outcome_calibration_v01 as cal
        from .outcome_feedback_consumer_v01 import require, identity, ordinary_review_v01, review_to_plain_v01
        validate_history_root_context_v01(history_key,root)
        query=SemanticResolveQuery(query_id=identity('discovery',dict(key=history_key,now=evaluation_time,transaction=transaction)),
            domain=history_key['domain_scope_id'],semantic_terms=('g34_history',),
            content_filters=dict(kind=HISTORY_PROFILE_G34,history_key=history_key),
            temporal_query=dict(as_of=g3._utc(evaluation_time)),worldstate={},require_root_review=True)
        discovery=resolve_semantic_candidates(self.drs,query,layers=('work',))
        evidence=dict(discovery_query=asdict(query),discovery=asdict(discovery),evaluations=[],ranked=[],opened=[])
        head=self.head_v01()
        if head is None: return None,evidence
        for candidate in discovery.candidates:
            if candidate.record_id!=head['record_id']: continue
            wrapper=self.drs.read_record('work',candidate.record_id)
            descriptor,meaning=self.current_descriptor_v01(head,history_key=history_key)
            require(wrapper['content']==dict(kind=HISTORY_PROFILE_G34,history_key=descriptor['history_key'],
                snapshot_id=head['snapshot_id'],record=address.meaning_record_to_plain_data_v01(meaning),
                semantic_keys=['g34_history'],root_final_ref=descriptor['root_review']['result']['decision_id'],worldstate_ref=descriptor['prior_id'],
                drs_record_is_truth=False,drs_hit_is_authority=False,drs_reuse_candidate_is_action_permission=False),'g34_drs_body_mismatch')
            pointer=meaning.artifact_pointers[0]
            now=evaluation_time
            current=memory.build_drs_temporal_query_v01(query_mode='CURRENT_DECISION',semantic_address_id=meaning.semantic_address.semantic_address_id,
                scope_fingerprint=identity('history_key',history_key),as_of=now,evaluation_time=now,
                evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',time_range_start=now,time_range_end=now+1,
                required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),freshness_policy_id=meaning.time_envelope.freshness_policy_id,
                max_age_seconds=meaning.time_envelope.ttl_seconds,domain=history_key['domain_scope_id'],risk_class='LOW',reuse_intent='CONTEXT',
                requested_reuse_classes=('CONTEXT_ONLY',),required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN',
                    'TIME_FITNESS','POLICY_COMPATIBILITY','SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),
                forbidden_changes=('POLICY_CHANGED',),policy_version=history_key['policy_semantics_version'],
                schema_versions=(HISTORY_PROFILE_G34,),owning_local_root_id=root)
            evaluation=memory.evaluate_drs_candidate_v01(semantic_address=meaning.semantic_address,query=current,meaning_record=meaning)
            evidence['evaluations'].append(memory.query_evaluation_state_to_plain_data_v01(evaluation))
            if candidate.blocked or not evaluation.eligible_for_ranking: continue
            ranked_candidate=memory.build_resolution_candidate_v01(query_id=current.query_id,semantic_address_id=meaning.semantic_address.semantic_address_id,
                meaning_record_id=meaning.meaning_record_id,query_evaluation_id=evaluation.query_evaluation_id,safe_summary=meaning.safe_summary,
                evidence_ref_ids=meaning.source_reference_ids,source_history_hash=evaluation.source_history_hash,action_history_binding_id=None,
                semantic_similarity_units=10000,freshness_units=evaluation.current_freshness_units,source_authority_prior_units=0,lineage_proximity_units=0,
                historical_utility_units=0,gt_advisory_prior_units=0,conflict_penalty_units=0,risk_penalty_units=0,retrieval_cost_units=0)
            ranked=memory.rank_eligible_drs_candidates_v01(query=current,query_evaluations=(evaluation,),candidates=(ranked_candidate,))
            evidence['ranked']=[memory.resolution_candidate_to_plain_data_v01(v) for v in ranked]
            require(bool(ranked),'g34_no_eligible_history')
            budget=memory.build_memory_descent_budget_v01(max_depth=1,max_records_opened=1,max_pointers_opened=1,max_artifacts_opened=1,
                max_bytes_opened=pointer.byte_length,max_lineage_edges=0,max_conflict_records=0)
            plan=memory.build_retrieval_plan_v01(query_id=current.query_id,semantic_address_id=meaning.semantic_address.semantic_address_id,
                proposed_record_ids=(meaning.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(pointer.pointer_id,),
                requested_descent_class='OPEN_ONE_ARTIFACT',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(pointer.access_policy_id,),reason_codes=())
            reviewed=ordinary_review_v01(root=root,transaction=current.query_id,candidates={plan.retrieval_plan_id:memory.retrieval_plan_to_plain_data_v01(plan)},
                selected=plan.retrieval_plan_id,scores={plan.retrieval_plan_id:1000000},evidence_ref=meaning.meaning_record_id,
                now=now,predicate='approve_controlled_memory_descent_plan_v01',
                subjects={plan.retrieval_plan_id:meaning.semantic_address.semantic_address_id})
            from hedgehog.kernel.integrity_replay_v01 import domain_separated_sha256_hex_v01
            root_hash=domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
                payload=canonical_json_bytes_v01(roots.root_decision_result_to_plain_dict_v01(reviewed[2])))
            request=memory.build_memory_descent_request_v01(retrieval_plan_id=plan.retrieval_plan_id,query_id=current.query_id,
                owning_local_root_id=root,root_kernel_id=reviewed[0].kernel_id,root_decision_input_id=reviewed[1].decision_input_id,
                root_decision_id=reviewed[2].decision_id,root_decision_hash=root_hash,requested_descent_class='OPEN_ONE_ARTIFACT',approved_descent_class='OPEN_ONE_ARTIFACT',
                proposed_budget_id=budget.memory_descent_budget_id,approved_budget=budget,approved_record_ids=(meaning.meaning_record_id,),
                approved_memory_pointer_ids=(),approved_artifact_pointer_ids=(pointer.pointer_id,))
            require(reviewed[2].decision=='ACCEPT','g34_payload_root_refusal')
            self.read_audit.append(dict(stage='ROOT_APPROVED',decision=reviewed[2].decision_id))
            payload_path=self.directory/'epochs'/(head['snapshot_id']+'.payload.json')
            require(payload_path.is_file() and not payload_path.is_symlink() and payload_path.stat().st_size<=524288,'g34_payload_bound')
            payload=payload_path.read_bytes()
            self.read_audit.append(dict(stage='PAYLOAD_READ',bytes=len(payload)))
            descent=memory.execute_local_memory_descent_v01(retrieval_plan=plan,proposed_budget=budget,descent_request=request,
                root_kernel=reviewed[0],root_decision_input=reviewed[1],root_decision_result=reviewed[2],source_records=(meaning,),
                artifact_payloads=((pointer.pointer_id,payload),))
            require(descent.limits_respected and not descent.reason_codes and descent.opened_record_ids==(meaning.meaning_record_id,),'g34_descent_refused')
            require(descent.opened_artifact_pointer_ids==(pointer.pointer_id,) and descent.bytes_opened==len(payload),'g34_exact_payload_open_required')
            self.read_audit.append(dict(stage='PUBLIC_OPEN_VALIDATED',bytes=descent.bytes_opened))
            value=HistorySnapshotV01(payload).to_plain_data()
            stored=self.read_v01(head['snapshot_id'],expected_sha256=head['body_sha256'])
            require(canonical_json_bytes_v01(stored['snapshot'])==payload and stored['meaning']==descriptor['meaning']
                and stored['review']==descriptor['root_review'],'g34_opened_payload_source')
            self.read_audit.append(dict(stage='NUMERIC_SOURCE_VALIDATED',snapshot=value['snapshot_id']))
            require(descent.safe_summaries[0]==value['snapshot_id'],'g34_opened_summary')
            require(self.head_v01()==head,'g34_head_changed_during_descent')
            evidence.update(query=memory.drs_temporal_query_to_plain_data_v01(current),plan=memory.retrieval_plan_to_plain_data_v01(plan),
                descent=memory.memory_descent_result_to_plain_data_v01(descent),review=review_to_plain_v01(reviewed),opened=list(descent.opened_record_ids),
                payload_sha256=hashlib.sha256(payload).hexdigest(),read_audit=list(self.read_audit))
            if all(e.source_profile_id==g3.ACTION_ADVICE_SOURCE_PROFILE_ID for e in self.sources.values()):
                # G36 retains the actual review for pure supplied-proof validation.
                evidence['root_records']=g3.g35_record_to_plain_v01(reviewed)
            update=cal.GTTrustUpdateV01(cal._canonical(value['updates'][-1])) if value['updates'] else None
            trust=cal.evaluate_gt_trust_at_v01(update,evaluation_time=now).to_plain_data()
            if trust['trust_status']!='USABLE':
                evidence['advice_refusal']=trust;return None,evidence
            old_env=dict(pt_created_at=g3._utc(value['evaluated_at']),kt_asof=g3._utc(value['evaluated_at']),et_observed_at=None,
                ct_session_anchor=value['snapshot_id'],ttl_seconds=value['valid_to']-value['evaluated_at'],freshness_class='static',
                valid_from=g3._utc(value['evaluated_at']),valid_to=g3._utc(value['valid_to']))
            historical=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:history:'+value['snapshot_id'],
                artifact_type='SemanticEvidence',schema_version='v1',transaction_id='g34:history:'+value['snapshot_id'],owner_root_id=root,
                source_component='g34_history',authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',
                payload=dict(snapshot_id=value['snapshot_id'],fold=value['fold'],prior=value['prior']),trace_refs=(value['snapshot_id'],),parent_refs=(),time_envelope=old_env)
            payload=dict(profile='G34_CURRENT_HISTORY_BRIDGE_V01',current_transaction_ref=transaction,current_local_root_ref=root,
                discovery_query_id=query.query_id,historical_ref=asdict(abi.kernel_artifact_to_canonical_ref_v01(historical)),
                head=head,history_key=history_key,query_id=current.query_id,descent_id=descent.memory_descent_result_id,
                prior=value['prior'],trust=trust,evaluated_at=now)
            env=dict(old_env,pt_created_at=g3._utc(now),kt_asof=g3._utc(now),ct_session_anchor=transaction,
                valid_from=g3._utc(now),ttl_seconds=value['valid_to']-now)
            bridge=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:bridge:'+identity('bridge',payload),artifact_type='SemanticEvidence',
                schema_version='v1',transaction_id=transaction,owner_root_id=root,source_component='g34_current_history',
                authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',payload=payload,trace_refs=(current.query_id,),parent_refs=(),time_envelope=env)
            evidence.update(historical_artifact=abi.kernel_artifact_to_plain_dict_v01(historical),bridge=abi.kernel_artifact_to_plain_dict_v01(bridge))
            opened=dict(snapshot_id=value['snapshot_id'],prior=value['prior'],trust=trust,bridge=bridge,
                evaluation_time=now,history_key=history_key,head=head,store=self,payload_sha256=evidence['payload_sha256'],
                descent=memory.memory_descent_result_to_plain_data_v01(descent))
            require(len(self._opened)<256,'g34_read_bound')
            self._opened[bridge.artifact_id]=canonical_json_bytes_v01(dict(
                snapshot_id=value['snapshot_id'],prior=value['prior'],trust=trust,bridge=abi.kernel_artifact_to_plain_dict_v01(bridge),
                evaluation_time=now,history_key=history_key,head=head,payload_sha256=opened['payload_sha256'],descent=opened['descent']))
            return opened,evidence
        return None,evidence

    def validate_opened_v01(self,opened,*,bridge,evaluation_time):
        from . import outcome_calibration_v01 as cal
        from .outcome_feedback_consumer_v01 import require
        require(type(opened) is dict and set(opened)=={'snapshot_id','prior','trust','bridge','evaluation_time','history_key','head','store','payload_sha256','descent'},'g34_opened_shape')
        require(opened['store'] is self and opened['evaluation_time']==evaluation_time,'g34_opened_context')
        data={k:v for k,v in opened.items() if k!='store'}
        data['bridge']=abi.kernel_artifact_to_plain_dict_v01(opened['bridge'])
        require(data['bridge']==abi.kernel_artifact_to_plain_dict_v01(bridge),'g34_opened_bridge')
        require(self._opened.get(bridge.artifact_id)==canonical_json_bytes_v01(data),'g34_actual_descent_required')
        require(self.head_v01()==opened['head'],'g34_opened_head_changed')
        payload=(self.directory/'epochs'/(opened['snapshot_id']+'.payload.json')).read_bytes()
        require(hashlib.sha256(payload).hexdigest()==opened['payload_sha256'],'g34_opened_payload_changed')
        value=self.read_v01(opened['snapshot_id'])['snapshot']
        require(canonical_json_bytes_v01(value)==payload,'g34_opened_body_changed')
        update=cal.GTTrustUpdateV01(cal._canonical(value['updates'][-1])) if value['updates'] else None
        require(value['prior']==opened['prior'] and cal.evaluate_gt_trust_at_v01(update,evaluation_time=evaluation_time).to_plain_data()==opened['trust'],
            'g34_opened_source_mismatch')
        return ()


@dataclass(frozen=True)
class NativeOutcomeWorkProofV01:
    """Independent live generic Work/Root objects retained by a trusted producer."""
    source: g3.NativeOutcomeSourceContextV01
    host: object
    program: object
    results: tuple
    common: dict
    review_bindings: tuple
    material: bytes
    review: tuple


def validate_native_work_proof_v01(proof):
    g3._require(type(proof) is NativeOutcomeWorkProofV01,'g32_native_proof_required')
    source=json.loads(proof.source.canonical);ctx=source['context'];fact=source['native']
    g3._require(fact['reached_boundary']=='WORK_ROOT','g32_genesis_requires_reached_work')
    ok,reasons=work.validate_work_program_result_v01(proof.program,proof.results,**proof.common,
        host_map={ctx['local_root_scope_id']:proof.host},review_bindings=proof.review_bindings)
    g3._require(ok,'g32_genesis_native_work:'+repr(reasons))
    artifact=work.work_program_result_to_artifact_v01(proof.program,proof.results,**proof.common,
        host_map={ctx['local_root_scope_id']:proof.host},review_bindings=proof.review_bindings)
    g3._require(artifact.artifact_id==fact['result_artifact_ref'] and artifact.owner_root_id==ctx['local_root_scope_id']
        and artifact.transaction_id==ctx['transaction_id'],'g32_genesis_native_binding')
    g3._require(hashlib.sha256(proof.material).hexdigest()==fact['material_sha256'],'g32_genesis_material')
    root_kernel,root_input,root_result=proof.review
    g3._require(not roots.validate_root_decision_result_v01(kernel=root_kernel,decision_input=root_input,result=root_result)
        and root_result.decision=='ACCEPT' and root_result.decision_id==fact['root_decision_ref']
        and root_result.target_root_id==ctx['local_root_scope_id'],'g32_genesis_native_root')
    claims=root_input.root_review_packet.synthesis_proposal.normalized_claims
    g3._require(len(claims)==1 and root_input.root_review_packet.runtime_topology_ref==proof.program.topology_artifact.artifact_id,'g32_genesis_native_topology')
    claim=semantic.semantic_work_to_plain_dict_v01(claims[0]);output=claim['object_or_value']
    material_output={item.parameter_name:item.value for item in proof.results[0].result.output}
    actual_output=json.loads(material_output['material'])
    g3._require(actual_output==output and actual_output['input_sha256']==hashlib.sha256(proof.material).hexdigest()
        and root_result.selected_candidate_id==claim['claim_id'],'g32_genesis_actual_output')
    g3._require(hashlib.sha256(canonical_json_bytes_v01(output)).hexdigest()==fact['output_sha256']
        and artifact.artifact_id in claim['provenance_refs'],'g32_genesis_native_consumption')
    return source


@dataclass(frozen=True)
class OutcomeRecordingReviewV01:
    candidate_canonical: bytes
    kernel: object
    decision_input: object
    decision_result: object


def _candidate(value,proof):
    source=validate_native_work_proof_v01(proof)
    reasons=g3.validate_outcome_feedback_against_sources_v01(value,source_bundle=proof.source,profile=g3.NATIVE_SOURCE_PROFILE_ID)
    g3._require(not reasons,'g32_genesis_feedback:'+repr(reasons))
    plain=g3.outcome_feedback_to_plain_data_v01(value)
    g3._require(plain['timestamp']<=time.time_ns()//10**9,'g32_genesis_future_evidence')
    occurrence=source['origin']['occurrence_id']
    record_id='g32genesis_'+g3._identity('g3_genesis_occurrence_v01',{'root':plain['local_root_scope_id'],'occurrence':occurrence,'purpose':PURPOSE})
    candidate=dict(purpose=PURPOSE,policy=POLICY,record_id=record_id,root=plain['local_root_scope_id'],transaction=plain['transaction_id'],
        occurrence_ref=occurrence,feedback_sha256=hashlib.sha256(value.canonical).hexdigest(),feedback_id=plain['feedback_id'],
        source_sha256=hashlib.sha256(proof.source.canonical).hexdigest(),subject=plain['advisory_subject_key'],
        history_key=plain['avf_history_key'],source_closure_ref=plain['source_closure_ref'])
    candidate['candidate_id']='g32:record:'+g3._identity('g3_genesis_candidate_v01',candidate)
    return candidate,plain


def review_outcome_recording_v01(value,*,native_proof):
    candidate,plain=_candidate(value,native_proof)
    root,transaction,cid=candidate['root'],candidate['transaction'],candidate['candidate_id']
    evidence_ref='g32:verified-source:'+candidate['source_sha256']
    req=semantic.build_semantic_work_request_v01(request_id='review:'+cid,transaction_id=transaction,target_root_id=root,
        runtime_topology_ref=native_proof.program.topology_artifact.artifact_id,bounded_context_refs=(evidence_ref,),
        permitted_actor_ids=('g32:local_record_validator',),permitted_contribution_modes=('DETERMINISTIC',),
        requested_subjects=(PURPOSE,),required_evidence_classes=('DEPENDENCY_EVIDENCE',),forbidden_claims=('authority_creation',))
    evidence=semantic.build_evidence_binding_v01(evidence_id='binding:'+evidence_ref,evidence_ref=evidence_ref,
        evidence_class='DEPENDENCY_EVIDENCE',source_component_id='g32:local_record_validator',provenance_ref=plain['source_closure_ref'],evidence_state='PRESENT')
    claim=semantic.build_normalized_claim_v01(claim_id=cid,subject=PURPOSE,predicate='authorize_g32_genesis_record_v01',
        object_or_value=candidate,time_envelope_ref='g32:observation:'+plain['observation_id'],provenance_refs=(evidence_ref,),
        evidence_refs=(evidence.evidence_id,),confidence_micros=1000000,source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution=semantic.build_actor_contribution_v01(contribution_id='contribution:'+cid,request_id=req.request_id,
        actor_id='g32:local_record_validator',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',
        bsep_projection_ref=native_proof.program.candidate.bsep_ref,scope=PURPOSE,bounded_context_refs=(evidence_ref,),claims=(claim,),
        evidence_bindings=(evidence,),constraint_bindings=(),uncertainty_bindings=(),requested_validators=('native_work_root','exact_source_feedback','genesis_scope'),forbidden_claims_observed=())
    packet=semantic.build_root_review_packet_from_contributions_v01(request=req,contributions=(contribution,),trust_profiles=trust.build_default_component_trust_profiles_v01())
    kernel=roots.build_root_decision_kernel_v01()
    inputs=roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id='g32:validated:'+candidate['feedback_sha256'],post_vv_passed=True,validated_candidate_ids=[cid],rejected_candidate_ids=[],
            required_evidence_refs=[evidence_ref],provided_evidence_refs=[evidence_ref],hard_failure_reasons=[]),
        gt_advisory=dict(advisory_id='g32:deterministic:'+cid,candidate_ids=[cid],selected_candidate_id=cid,score_micros_by_candidate={cid:1000000},
            source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',
            target_artifact_type='RootDecision',advisory_only=True,creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=POLICY,identity_passed=True,scope_passed=True,hard_policy_passed=True,allow_accept=True,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=False,user_permission_present=False,permission_scope_valid=True,permission_ref=None),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref='g32:observation:'+plain['observation_id']),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result=roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    review=OutcomeRecordingReviewV01(g3._canonical(candidate),kernel,inputs,result)
    validate_recording_review_v01(value,native_proof=native_proof,review=review)
    return review


def validate_recording_review_v01(value,*,native_proof,review):
    candidate,plain=_candidate(value,native_proof)
    g3._require(type(review) is OutcomeRecordingReviewV01 and review.candidate_canonical==g3._canonical(candidate),'g32_record_exact_candidate')
    g3._require(not roots.validate_root_decision_kernel_v01(review.kernel)
        and not roots.validate_root_decision_input_v01(kernel=review.kernel,decision_input=review.decision_input)
        and not roots.validate_root_decision_result_v01(kernel=review.kernel,decision_input=review.decision_input,result=review.decision_result),'g32_record_actual_root_validation')
    result=review.decision_result;inputs=review.decision_input
    claims=inputs.root_review_packet.synthesis_proposal.normalized_claims
    g3._require(result.decision=='ACCEPT' and result.target_root_id==candidate['root'] and inputs.transaction_id==candidate['transaction']
        and result.selected_candidate_id==candidate['candidate_id'] and len(claims)==1,'g32_record_root_scope')
    claim=semantic.semantic_work_to_plain_dict_v01(claims[0])
    g3._require(claim['object_or_value']==candidate and claim['predicate']=='authorize_g32_genesis_record_v01'
        and claim['subject']==PURPOSE and roots.root_decision_input_to_plain_dict_v01(inputs)['policy_state']['policy_id']==POLICY,'g32_record_root_consumption')
    return candidate,plain


class OutcomeHistoryGenesisV01:
    """One explicit external local store; no default path and no global state."""
    def __init__(self,directory):
        path=Path(directory)
        g3._require(path.is_absolute() and not path.exists(),'g32_new_external_store_required')
        path.mkdir(parents=True)
        self.directory=path
        self.drs=LocalDRS(path/'drs')
        self._accepted=None

    def query_v01(self,*,subject,history_key,as_of):
        g3._keys(subject,g3._SUBJECT_FIELDS);g3._keys(history_key,g3._HISTORY_FIELDS)
        query=SemanticResolveQuery(query_id='g32:query:'+g3._identity('g3_genesis_query_v01',{'subject':subject,'history_key':history_key,'as_of':as_of}),
            domain=subject['domain_scope_id'],semantic_terms=(subject['local_root_scope_id'],subject['route_family_id'],subject['policy_semantics_version']),
            content_filters={'subject_fields':subject,'history_key':history_key},temporal_query={'as_of':g3._utc(as_of),'query_mode':'historical'},
            require_root_review=True,max_candidates=8)
        return query,resolve_semantic_candidates(self.drs,query,layers=('work',))

    def record_v01(self,value,*,native_proof,review):
        candidate,plain=validate_recording_review_v01(value,native_proof=native_proof,review=review)
        if self._accepted is not None:
            g3._require(self._accepted==review.candidate_canonical,'g32_genesis_duplicate_or_non_genesis')
            return self.readback_v01(value,native_proof=native_proof,review=review)
        payload_dir=self.directory/'evidence';payload_dir.mkdir()
        (payload_dir/'feedback.json').write_bytes(value.canonical)
        (payload_dir/'source.json').write_bytes(native_proof.source.canonical)
        # The existing resolver's duplicate signature requires a scalar subject_key.
        # Full typed fields remain independently searchable and payload-bound.
        summary=dict(evidence_class='EVIDENCE_ONLY',purpose=PURPOSE,
            subject_key=g3._identity('g3_history_subject_v01',candidate['subject']),subject_fields=candidate['subject'],history_key=candidate['history_key'],
            occurrence_ref=candidate['occurrence_ref'],feedback_id=plain['feedback_id'],proposal_assessment=plain['proposal_assessment'],
            task_outcome=plain['task_outcome'],feedback_path='evidence/feedback.json',feedback_sha256=candidate['feedback_sha256'],
            source_path='evidence/source.json',source_sha256=candidate['source_sha256'],current_reuse='NOT_IMPLEMENTED',sample_state='GENESIS_NOT_WARM')
        record=write_semantic_record(self.drs,SemanticDRSRecordInput(record_id=candidate['record_id'],domain=plain['domain'],
            content=summary,semantic_keys=(plain['local_root_scope_id'],plain['advisory_subject_key']['route_family_id'],plain['advisory_subject_key']['policy_semantics_version']),
            record_type='root_reviewed_semantic_outcome',time_envelope=plain['time_envelope'],root_final_ref=review.decision_result.decision_id,
            source_refs=({'source':'G32_NATIVE_REVIEWED_WORK','source_id':plain['observation_id']},)))
        self._accepted=review.candidate_canonical
        self._record_bytes=canonical_json_bytes_v01(record)
        return self.readback_v01(value,native_proof=native_proof,review=review)

    def readback_v01(self,value,*,native_proof,review):
        candidate,plain=validate_recording_review_v01(value,native_proof=native_proof,review=review)
        g3._require(self._accepted==review.candidate_canonical,'g32_record_independent_anchor')
        for name,expected in (('feedback.json',value.canonical),('source.json',native_proof.source.canonical)):
            path=self.directory/'evidence'/name
            g3._require(path.is_file() and not path.is_symlink() and path.read_bytes()==expected,'g32_persisted_payload_changed')
        record=self.drs.read_record('work',candidate['record_id'])
        g3._require(canonical_json_bytes_v01(record)==self._record_bytes,'g32_persisted_record_changed')
        return record
