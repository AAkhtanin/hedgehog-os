"""Football metadata descent using the public numerical donor's native sequence."""
from datetime import datetime, timezone
from hedgehog.drs import LocalDRS
from hedgehog import local_drs_resolver as resolver, drs_semantic_address_v01 as address
from hedgehog import drs_memory_resolution_v01 as memory
from hedgehog.kernel import integrity_replay_v01 as integrity, root_decision_v01 as roots
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n
from candidate_domain.native import review
from candidate_domain.storage import save

def persist_pointer(folder,pointer):
    resolver.write_semantic_record(LocalDRS(folder),resolver.SemanticDRSRecordInput(
        record_id=pointer['pointer_id'],domain='FOOTBALL',content=dict(kind='football_pointer',pointer=pointer),
        semantic_keys=('football','pointer')))

def descent(pointer,root,folder,now,source_end):
    c.require(now<source_end,'pointer_source_expired')
    policy='football.pointer.context.v01'; domain='FOOTBALL'
    summary='Bounded synthetic football venue offer metadata.'
    addr=address.build_semantic_address_v01(namespace='football',domain=domain,subject_class='external_pointer',
        intent_class='context_lookup',meaning_schema_id='football.pointer_metadata',meaning_schema_version='v01')
    env=n.rebuilt(address.build_drs_time_envelope_v01,pointer['time_envelope'])
    first=review(root,'transaction:football:pointer:'+c.sha(pointer),'candidate:football:pointer:'+c.sha(pointer),
        addr.semantic_address_id,dict(metadata_only=pointer['safe_summary']==summary,
        bounded=len(c.canonical(pointer))<=c.POINTER_MAX),dict(pointer=pointer),now,folder,'pointer_review',
        window=(pointer['time_envelope']['valid_from'],source_end))
    c.require(first[2].decision=='ACCEPT','pointer_review_refused')
    records=[]; drs=LocalDRS(folder/'drs')
    for accepted in (False,True):
        auth=address.build_drs_authority_envelope_v01(
            authority_class='ROOT_ACCEPTED_CONTEXT' if accepted else 'CONNECTOR_OBSERVATION',
            owning_local_root_id=root if accepted else None,
            source_root_decision_input_id=first[1].decision_input_id if accepted else None,
            source_root_decision_id=first[2].decision_id if accepted else None,
            source_root_decision_hash=c.sha(roots.root_decision_result_to_plain_dict_v01(first[2])) if accepted else None,
            authority_scope_fingerprint=c.sha(pointer),root_acceptance_state='ACCEPTED_CONTEXT' if accepted else 'UNREVIEWED',
            recording_component='football:connector')
        record=address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
            safe_summary=summary,semantic_tags=('football','pointer'),
            resonance_reason='Foreign metadata retained for local context review.',
            memory_pointers=(),artifact_pointers=(),source_reference_ids=(pointer['source_record_ref'],),
            lineage_edges=(),time_envelope=env,authority_envelope=auth,persistent_lifecycle_state='ACTIVE',
            risk_hints=(),conflict_hints=(),reuse_policy_class='CONTEXT_ONLY',policy_version=policy,
            schema_versions=(policy,),content_fingerprint=c.sha(pointer),recording_component='football:connector')
        def stamp(t):
            return datetime.fromtimestamp(t,timezone.utc).isoformat()
        t=pointer['time_envelope']
        resolver.write_semantic_record(drs,resolver.SemanticDRSRecordInput(record_id=record.meaning_record_id,
            domain=domain,content=dict(kind='pointer',record=address.meaning_record_to_plain_data_v01(record)),
            semantic_keys=('football','pointer'),time_envelope=dict(pt_created_at=stamp(t['pt_created_at']),
            kt_asof=stamp(t['kt_as_of']),et_observed_at=stamp(t['et_observed_at']),ct_session_anchor='football:session',
            ttl_seconds=t['ttl_seconds'],freshness_class='static',valid_from=stamp(t['valid_from']),valid_to=stamp(source_end))))
        records.append(record.meaning_record_id)
    drs=LocalDRS(folder/'drs')
    resolved=resolver.resolve_semantic_candidates(drs,resolver.SemanticResolveQuery(
        query_id='football:lookup:'+c.sha(pointer),domain=domain,semantic_terms=('football','pointer'),
        content_filters=dict(kind='pointer'),max_candidates=4,require_root_review=True),layers=('work',))
    save(folder/'pointer_lookup.json',n.plain(resolved))
    c.require(set(records)=={v.record_id for v in resolved.candidates},'persisted_pointer_resolution')
    evaluations=[]
    for record_id in records:
        stored=drs.read_record('work',record_id)['content']['record']
        source=dict(stored,semantic_address=n.rebuilt(address.build_semantic_address_v01,stored['semantic_address']),
            time_envelope=n.rebuilt(address.build_drs_time_envelope_v01,stored['time_envelope']),
            authority_envelope=n.rebuilt(address.build_drs_authority_envelope_v01,stored['authority_envelope']))
        record=n.rebuilt(address.build_meaning_record_v01,source)
        c.require(address.meaning_record_to_plain_data_v01(record)==stored,'persisted_meaning_identity')
        query=memory.build_drs_temporal_query_v01(query_mode='CURRENT_DECISION',semantic_address_id=addr.semantic_address_id,
            scope_fingerprint=c.sha(pointer),as_of=now,evaluation_time=now,evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',
            time_range_start=now,time_range_end=now+1,required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),
            freshness_policy_id=env.freshness_policy_id,max_age_seconds=pointer['time_envelope']['ttl_seconds'],
            domain=domain,risk_class='LOW',reuse_intent='CONTEXT',requested_reuse_classes=('CONTEXT_ONLY',),
            required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN','TIME_FITNESS',
            'POLICY_COMPATIBILITY','SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),
            forbidden_changes=('POLICY_CHANGED',),policy_version=policy,schema_versions=(policy,),owning_local_root_id=root)
        evaluation=memory.evaluate_drs_candidate_v01(semantic_address=addr,query=query,meaning_record=record)
        evaluations.append(memory.query_evaluation_state_to_plain_data_v01(evaluation))
    c.require(not evaluations[0]['eligible_for_ranking'] and evaluations[1]['eligible_for_ranking'],'pointer_authority_states')
    budget=memory.build_memory_descent_budget_v01(max_depth=0,max_records_opened=1,max_pointers_opened=0,
        max_artifacts_opened=0,max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
    plan=memory.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=addr.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),
        requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(),reason_codes=())
    rev=review(root,query.query_id,plan.retrieval_plan_id,addr.semantic_address_id,
        dict(eligible=evaluation.eligible_for_ranking,metadata_only=record.safe_summary==summary),
        memory.retrieval_plan_to_plain_data_v01(plan),now,folder,'descent_review',window=(now,source_end),
        predicate='approve_controlled_memory_descent_plan_v01')
    c.require(rev[2].decision=='ACCEPT','descent_review_refused')
    rh=integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
        payload=c.canonical(roots.root_decision_result_to_plain_dict_v01(rev[2])))
    req=memory.build_memory_descent_request_v01(retrieval_plan_id=plan.retrieval_plan_id,query_id=query.query_id,
        owning_local_root_id=root,root_kernel_id=rev[0].kernel_id,root_decision_input_id=rev[1].decision_input_id,
        root_decision_id=rev[2].decision_id,root_decision_hash=rh,requested_descent_class='SUMMARY_ONLY',
        approved_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,approved_budget=budget,
        approved_record_ids=(record.meaning_record_id,),approved_memory_pointer_ids=(),approved_artifact_pointer_ids=())
    result=memory.execute_local_memory_descent_v01(retrieval_plan=plan,proposed_budget=budget,descent_request=req,
        root_kernel=rev[0],root_decision_input=rev[1],root_decision_result=rev[2],source_records=(record,))
    c.require(result.limits_respected and not result.reason_codes and result.safe_summaries==(summary,),'descent_result')
    save(folder/'pointer_descent.json',dict(resolver=n.plain(resolved),evaluations=evaluations,
        plan=memory.retrieval_plan_to_plain_data_v01(plan),request=n.plain(req),result=n.plain(result)))
    return rev[2].decision_id
