"""Pure contextual checks for retained Atlas history epochs; no store or Root calls."""
import hashlib
import json
from pathlib import Path
from hedgehog import outcome_calibration_v01 as cal, outcome_feedback_v01 as feedback
from hedgehog import outcome_feedback_history_v01 as history, outcome_feedback_consumer_v01 as consumer
from hedgehog.kernel import root_decision_v01 as roots


def review_from_plain_v01(value):
    """Reconstruct only closed Root data, then validate; never decide or open a store."""
    import dataclasses
    import types
    import typing
    from hedgehog.kernel import semantic_work_v01 as semantic
    allowed = set(feedback._g35_record_types_v01().values())
    def decode(kind, data):
        origin = typing.get_origin(kind); args = typing.get_args(kind)
        if origin in (typing.Union, types.UnionType):
            if data is None and type(None) in args: return None
            kinds = [k for k in args if k is not type(None)]
            require(len(kinds)==1, 'atlas_root_plain_union')
            return decode(kinds[0],data)
        if origin is tuple:
            require(type(data) is list, 'atlas_root_plain_tuple')
            return tuple(decode(args[0],v) for v in data)
        if dataclasses.is_dataclass(kind):
            require(kind in allowed and type(data) is dict and set(data)=={f.name for f in dataclasses.fields(kind)}, 'atlas_root_plain_shape')
            hints=typing.get_type_hints(kind)
            fields={k:decode(hints[k],v) for k,v in data.items()}
            if kind is semantic.NormalizedClaimV01:
                authority=fields.pop('authority_class')
                result=semantic.build_normalized_claim_v01(**fields)
                require(result.authority_class==authority,'atlas_root_plain_claim_authority')
                return result
            if kind is roots.RootDecisionInputV01:
                expected=fields.pop('decision_input_id')
                result=roots.build_root_decision_input_v01(**fields)
                require(result.decision_input_id==expected,'atlas_root_plain_input_id')
                return result
            return kind(**fields)
        return data
    require(set(value)=={'kernel','input','result'},'atlas_root_plain_review')
    review=tuple(decode(kind,value[key]) for kind,key in ((roots.RootDecisionKernelV01,'kernel'),(roots.RootDecisionInputV01,'input'),(roots.RootDecisionResultV01,'result')))
    require(consumer.review_to_plain_v01(review)==value,'atlas_root_plain_roundtrip')
    require(not roots.validate_root_decision_result_v01(kernel=review[0],decision_input=review[1],result=review[2]),'atlas_root_plain_validation')
    return review

canonical=consumer.canonical
require=consumer.require


def storage_projection_v01(directory, snapshots):
    result={}
    for snapshot in snapshots:
        key=snapshot['snapshot_id']
        require(len(key)==64 and all(c in '0123456789abcdef' for c in key),'atlas_history_storage_key')
        result[key]={name:(Path(directory)/'epochs'/(key+suffix)).read_text() for name,suffix in
            (('body','.json'),('descriptor','.descriptor.json'),('payload','.payload.json'))}
    return result


def validate_snapshot_v01(snapshot, events):
    history.HistorySnapshotV01(canonical(snapshot)).to_plain_data()
    history.validate_history_delivery_refs_v01(snapshot['event_refs'],events)
    selected=tuple(events[ref] for ref in snapshot['event_refs'])
    require(snapshot['corrections']==[], 'atlas_history_unreviewed_correction')
    require(snapshot['source_pins']=={ref:hashlib.sha256(events[ref].source_canonical).hexdigest()
        for ref in set(snapshot['event_refs'])}, 'atlas_history_source_pins')
    fold=cal.bounded_gt_event_fold_v01(selected,evaluated_at=snapshot['evaluated_at'])
    require(snapshot['fold']==fold.to_plain_data() and snapshot['updates']==[v.to_plain_data() for v in fold.updates],
            'atlas_history_complete_fold')
    require(snapshot['prior']==cal.fold_avf_history_prior_v01(selected,evaluated_at=snapshot['evaluated_at']).to_plain_data(),
            'atlas_history_complete_prior')
    windows=[feedback._source(cal._source_bundle(e),e.source_profile_id)[0]['native']['time_envelope'] for e in selected]
    require(snapshot['valid_from']==max(cal._iso_epoch(w['valid_from']) for w in windows)
        and snapshot['valid_to']==min(cal._iso_epoch(w['valid_to']) for w in windows), 'atlas_history_source_window')
    from hedgehog.domains.supplier_water_filter import adversarial_feedback_v01 as supplier
    if all(e.source_profile_id==supplier.PROFILE for e in selected):
        expected=[supplier.provenance_row_v01(supplier.ActionAdviceSourceContextV01(e.source_canonical),e) for e in selected]
        require(snapshot.get('review_source_projections')==expected,'atlas_history_review_sources')
    else:
        require('review_source_projections' not in snapshot,'atlas_history_foreign_review_sources')


def validate_recording_review_v01(snapshot, review):
    kernel,inputs,result=review
    require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'atlas_history_root_validation')
    root=snapshot['prior']['history_key']['local_root_scope_id'];key=snapshot['snapshot_id']
    proposal=dict(snapshot_id=key,expected_head=snapshot['predecessor'],source_pins=snapshot['source_pins'],
        fold_id=snapshot['fold']['fold_id'],prior_id=snapshot['prior']['prior_id'],corrections=snapshot['corrections'],
        root=root,epoch=snapshot['epoch'],evaluated_at=snapshot['evaluated_at'])
    require(result.decision=='ACCEPT' and result.target_root_id==inputs.target_root_id==root
        and result.transaction_id==inputs.transaction_id=='g34:history:'+key and result.selected_candidate_id==key,
        'atlas_history_recording_scope')
    raw=roots.root_decision_input_to_plain_dict_v01(inputs)
    claims=raw['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(len(claims)==1 and claims[0]['claim_id']==key and claims[0]['object_or_value']==proposal
        and claims[0]['predicate']=='g34_record_exact_history' and claims[0]['provenance_refs']==[key]
        and key in raw['post_vv_bundle']['provided_evidence_refs'], 'atlas_history_recording_material')


def validate_epoch_v01(snapshot, head, review, storage):
    require(set(head)=={'snapshot_id','body_sha256','record_id','descriptor_sha256'},'atlas_history_head_shape')
    require(head['snapshot_id']==snapshot['snapshot_id'],'atlas_history_head_snapshot')
    record=storage[snapshot['snapshot_id']]
    require(set(record)=={'body','descriptor','payload'},'atlas_history_storage_shape')
    body=json.loads(record['body']);descriptor=json.loads(record['descriptor'])
    require(set(body)=={'snapshot','review','meaning'} and body['snapshot']==snapshot
        and body['review']==consumer.review_to_plain_v01(review),'atlas_history_epoch_body')
    require(record['payload'].encode()==canonical(snapshot),'atlas_history_epoch_payload')
    require(hashlib.sha256(record['body'].encode()).hexdigest()==head['body_sha256']
        and hashlib.sha256(record['descriptor'].encode()).hexdigest()==head['descriptor_sha256'],'atlas_history_head_bytes')
    require(descriptor==dict(snapshot_id=snapshot['snapshot_id'],history_key=snapshot['prior']['history_key'],meaning=body['meaning'],
        root_review=body['review'],body_sha256=head['body_sha256'],prior_id=snapshot['prior']['prior_id']), 'atlas_history_descriptor')
    require(body['meaning']['meaning_record_id']==head['record_id'],'atlas_history_meaning_record')


def validate_chain_v01(*, initial, initial_head, initial_review, deliveries, events, storage):
    validate_snapshot_v01(initial,events)
    validate_recording_review_v01(initial,initial_review)
    validate_epoch_v01(initial,initial_head,initial_review,storage)
    current,head=initial,initial_head
    for row in deliveries:
        require(row['before']==current and row['head_before']==head,'atlas_history_sequential_before')
        after=row['after']
        require(after['predecessor']==head and after['epoch']==current['epoch']+1
            and after['event_refs']==current['event_refs']+[row['event_ref']], 'atlas_history_predecessor')
        validate_snapshot_v01(after,events)
        review=feedback.g35_record_from_plain_v01(json.loads(row['review']))
        validate_recording_review_v01(after,review)
        validate_epoch_v01(after,row['head_after'],review,storage)
        current,head=after,row['head_after']
    require(set(storage)=={initial['snapshot_id'],*(r['after']['snapshot_id'] for r in deliveries)},'atlas_history_storage_inventory')
    return current,head
