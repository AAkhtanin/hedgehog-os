"""Source-owned producer, publication and separate current booking projections."""
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_exchange_v01 as x, gate5_native_v01 as n
from candidate_domain.domain import need, Refusal, verify_producer, planning_equal, inventory_check
from candidate_domain.native import perform, review
from candidate_domain.profile import profile, SCHEMA, SUMMARY
from candidate_domain.storage import read, save, state, history_path
from candidate_domain.memory import persist_pointer
from candidate_domain.effect import book, reconcile
from candidate_domain.policy import consumer_policy

def envelope(now,ttl):
    return c.drs.drs_time_envelope_to_plain_data_v01(c.drs.build_drs_time_envelope_v01(
        pt_created_at=now,kt_as_of=now,et_observed_at=now,ct_context_anchor=now,ttl_seconds=ttl,
        valid_from=now,valid_to=now+ttl,source_observed_at=now,source_reported_at=now,
        system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:football:source'))

def selected_history(root,r):
    old=read(history_path(root,r))
    need(old is not None,'original_offer_history_missing','CURRENT_STATUS_UNKNOWN')
    need(planning_equal(r,old['body']['offer']['request']),'changed_original_offer_request')
    return old

def build(r,i,p,root,folder,cap,keys,public):
    need(p['peer_root'] in p['recipients'] and p['publish_enabled'],'publication_audience_refused')
    if r['operation']=='VERIFY_EXISTING':
        need(p['release_enabled'],'history_release_refused')
        history=reconcile(root,r)
        need(history is not None,'booking_history_missing','CURRENT_STATUS_UNKNOWN')
        return dict(history=history)
    if r['operation']=='CONFIRM_MOCK_BOOKING':
        history=reconcile(root,r)
        if history is not None:
            need(p['release_enabled'],'history_release_refused')
            return dict(history=history)
        old=selected_history(root,r)
        previous=old['body']
        need(p['status']!='UNAVAILABLE','current_status_unavailable','CURRENT_STATUS_UNKNOWN')
        need(p['status']=='ACTIVE' and p['release_enabled'],'confirmation_source_not_active')
        booking=book(r,i,previous,p,root,folder)
        producer=old['work']; e=previous['offer']
        save(folder/'venue_work.json',producer)
        save(folder/'original_source_inputs.json',old['original_inputs'])
        save(folder/'original_source_review.json',old['source_review'])
        source_claim=dict(request_sha256=c.sha(r),inventory_sha256=c.sha(i),consumed_offer=e,
            source_work_ref=producer['artifact']['artifact_id'],booking=booking,
            previous_source_ref=previous['source_record_ref'],previous_review_ref=previous['source_review_ref'])
        now=x.clock()
        original=e['request']
        record=consumer_policy(dict(p,local_root=p['peer_root'],peer_root=p['local_root']),public,r,original)['source_record_ref']
        local=review(p['local_root'],'transaction:football:confirmation:'+c.sha(r),
            'candidate:football:confirmation:'+c.sha(booking),record,
            dict(receipt_readback=reconcile(root,r) is not None,original_work=producer['outputs']['offer_json']==c.canonical(e).decode()),
            source_claim,now,folder,'source_review')
        need(local[2].decision=='ACCEPT','confirmation_source_review_refused','CURRENT_STATUS_UNKNOWN')
        original=e['request']
        record=consumer_policy(dict(p,local_root=p['peer_root'],peer_root=p['local_root']),public,r,original)['source_record_ref']
        body=dict(previous,source_record_ref=record,source_review_ref=local[2].decision_id,booking=booking,
            source_lineage_refs=[previous['source_record_ref'],previous['source_review_ref'],producer['artifact']['artifact_id']])
        source_review=n.root_plain(local)
        original_inputs=old['original_inputs']
        origin=dict(classification='HISTORICAL_PRODUCER_WITH_SEPARATE_CURRENT_CONFIRMATION',
                    original_body=previous,original_source_review=old['source_review'])
        save(folder/'producer_origin.json',origin)
        calls=0
    else:
        need(r['operation']=='FIND_OFFER','clarification_requested','CLARIFY')
        inventory_check(i,r)
        ledger=read(root/'registry.json',dict(records=[],idempotency={}))
        fields={f['field_id']:f for f in i['fields']}
        need(all(s['field_id'] in fields and any(lo<=s['start_utc']<s['end_utc']<=hi
                 for lo,hi in fields[s['field_id']]['occupied_utc'])
                 for s in ledger['records'] if s['venue_ref']==r['venue_ref']),
             'operator_inventory_missing_committed_occupancy','CURRENT_STATUS_UNKNOWN')
        old=read(history_path(root,r))
        if old is not None and old['body']['offer']['schedule_revision']==i['revision']:
            need(old['original_inputs']==dict(request=r,inventory=i),'same_source_revision_changed_inputs')
            body=old['body']; producer=old['work']; source_review=old['source_review']
            original_inputs=old['original_inputs']; original=r; calls=0
            c.temporal(body['time_envelope'],x.clock(),dict(max_source_age=p['max_source_age'],max_validity_horizon=300))
            save(folder/'venue_work.json',producer); save(folder/'source_review.json',source_review)
            save(folder/'producer_origin.json',dict(classification='SAVED_ORIGINAL_PRODUCER',body_sha256=c.sha(body)))
        else:
            producer=perform('venue',r,i,p['local_root'],'task:football:produce:'+c.sha(dict(request=r,inventory=i)),evidence_folder=folder)
            save(folder/'venue_work.json',producer)
            e=c.decode(producer['outputs']['offer_json'].encode()); verify_producer(r,i,e)
            now=x.clock(); original=r
            record=consumer_policy(dict(p,local_root=p['peer_root'],peer_root=p['local_root']),public,r,r)['source_record_ref']
            claim=dict(request_sha256=c.sha(r),inventory_sha256=c.sha(i),consumed_offer=e,
                source_work_ref=producer['artifact']['artifact_id'],booking=None,previous_source_ref=None,previous_review_ref=None)
            local=review(p['local_root'],'transaction:football:source:'+c.sha(r),producer['artifact']['artifact_id'],record,
                dict(native_completed=producer['attempts']==1,original_request=e['request']==r,
                     source_revision=e['schedule_revision']==i['revision']),claim,now,folder,'source_review')
            need(local[2].decision=='ACCEPT','source_review_refused')
            source_review=n.root_plain(local)
            body=dict(version='g51.body.v01',source_record_ref=record,source_revision=e['offer_revision'],
                source_work_ref=producer['artifact']['artifact_id'],source_review_ref=local[2].decision_id,
                time_envelope=envelope(now,p['ttl_seconds']),ttl_base='pt_created_at',
                source_lineage_refs=[producer['artifact']['artifact_id']],publisher=p['local_root'],recipient=p['peer_root'],
                request_sha256=c.sha(r),offer=e,booking=None)
            original_inputs=dict(request=r,inventory=i); calls=1
        save(folder/'original_source_inputs.json',original_inputs)
    c.validate('body',body,profile=profile())
    manifest=c.with_id('manifest',dict(version='g51.manifest.v01',publisher=p['local_root'],
        source_revision=body['source_revision'],source_refs=[body['source_record_ref'],body['source_work_ref'],body['source_review_ref']],
        declared_schema=SCHEMA,files=[dict(path='body.json',bytes=len(c.canonical(body)),sha256=c.sha(body))]))
    c.validate('manifest',manifest,profile=profile())
    object_id=consumer_policy(dict(p,local_root=p['peer_root'],peer_root=p['local_root']),public,r,original)['object_id']
    pointer=c.with_id('pointer',dict(version='g51.pointer.v01',publisher_root_id=p['local_root'],publisher_key_id=cap.key_id,
        semantic_address=dict(namespace='football',domain='FOOTBALL',subject_class='venue_offer',intent_class='context_lookup',
                              schema_id=SCHEMA,schema_version='v01'),
        source_record_ref=body['source_record_ref'],source_revision=body['source_revision'],source_review_ref=body['source_review_ref'],
        body_sha256=c.sha(body),body_bytes=len(c.canonical(body)),media_type='application/json',
        artifact_manifest_ref=manifest['manifest_id'],safe_summary=SUMMARY,published_scope=dict(domain='FOOTBALL'),
        allowed_use_classes=['LOCAL_CONTEXT'],forbidden_use_classes=['ACTION'],recipient_scope=[p['peer_root']],
        time_envelope=body['time_envelope'],source_lineage_refs=body['source_lineage_refs'],access_policy_ref='policy:football:source',
        revocation_stream_id='stream:football:'+c.sha(dict(record=body['source_record_ref'],revision=body['source_revision'])),
        transport_object_id=object_id,creates_authority=False,creates_permission=False))
    c.validate('pointer',pointer,profile=profile())
    now=x.clock(); end=c.temporal(body['time_envelope'],now,dict(max_source_age=p['max_source_age'],max_validity_horizon=300))
    publication=review(p['local_root'],'transaction:football:publication:'+c.sha(body),pointer['pointer_id'],
        body['source_record_ref'],dict(owner_publish=p['publish_enabled'],source_binding=body['source_review_ref']==source_review['result']['decision_id'],
        bounded=len(c.canonical(pointer))<=c.POINTER_MAX),
        dict(pointer=pointer,source_review_ref=body['source_review_ref']),now,folder,'publication_review',
        window=(body['time_envelope']['valid_from'],end))
    need(publication[2].decision=='ACCEPT','publication_review_refused')
    descriptor=c.sign(cap,keys,'POINTER',pointer,manifest['manifest_id'].split(':')[1])
    for name,value in (('offer_body',body),('manifest',manifest),('descriptor',descriptor)):
        save(folder/(name+'.json'),value)
    persist_pointer(root/'source_drs',pointer)
    stored=dict(body=body,work=producer,source_review=source_review,original_inputs=original_inputs)
    save(root/'archives'/(c.sha(body)+'.json'),stored)
    if r['operation']=='FIND_OFFER':
        state(history_path(root,r),stored)
    return dict(body=body,manifest=manifest,descriptor=descriptor,source_calls=calls)

def history_projection(history):
    saved=history['saved']; ledger=history['readback']
    return dict(booking=saved['booking'],entry=ledger['idempotency'][saved['native_key']],
        native_key=saved['native_key'],readback_sha256=c.sha(ledger),body_sha256=c.sha(saved['body']),
        receipt_ref=saved['receipt']['artifact_id'],request_sha256=c.sha(saved['request']))
