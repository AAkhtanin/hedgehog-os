"""LocalDRS safe summaries with current eligibility and independent Root descent."""
from dataclasses import asdict
import json
from pathlib import Path
from hedgehog.drs import LocalDRS
from hedgehog import local_drs_resolver as resolver,drs_semantic_address_v01 as address,drs_memory_resolution_v01 as memory
from hedgehog.kernel import integrity_replay_v01 as integrity
from . import native_contracts_v01 as c,native_adapter_v01 as n,math_v01 as math

DOMAIN='WEDDING_SEATING'
POLICY='wedding.context_only.v01'
def dependencies(owner):return dict(problem_ref=owner.problem().content_id,profile=owner.profile,owner=owner.problem().to_plain_v01()['owner_root_id'],policy=POLICY)

class WeddingMemoryV01:
    def __init__(self,directory):
        self.drs=LocalDRS(Path(directory));self.records={};self.events=[]

    def remember_v01(self,run):
        run.validate_current(run.owner)
        return self._write(run.owner,run.output,'accepted_plan',run.evidence['now'],run.final_review,run.evidence['artifact']['artifact_id'])

    def remember_negative_v01(self,owner,now):
        witness=math.contradiction_witness_v01(owner.problem())
        c.require(bool(witness),'negative_requires_direct_witness')
        value=dict(status='DIRECT_CONTRADICTION',conditions=witness)
        ref=c.identity('negative',value);root=owner.problem().to_plain_v01()['owner_root_id']
        review=n.root_review(root,'transaction:'+owner.request_ref,ref,owner.request_ref,dict(original_pair=bool(witness)),ref,'wedding:negative:bsep','wedding:negative:topology',now,claim_value=value)
        return self._write(owner,value,'negative_context',now,review,owner.problem().content_id)

    def _write(self,owner,value,kind,now,review,source_ref):
        dep=dependencies(owner);root=dep['owner'];material=dict(kind=kind,dependencies=dep,value=value,source_ref=source_ref)
        addr=address.build_semantic_address_v01(namespace='wedding',domain=DOMAIN,subject_class=kind,intent_class='context_lookup',meaning_schema_id='wedding.safe_context',meaning_schema_version='v0.1')
        env=address.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=now,ct_context_anchor=now,ttl_seconds=3600,valid_from=now,valid_to=now+3600,
            source_observed_at=now,source_reported_at=now,system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:wedding:context')
        auth=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=root,source_root_decision_input_id=review[1].decision_input_id,
            source_root_decision_id=review[2].decision_id,source_root_decision_hash=c.digest(n.roots.root_decision_result_to_plain_dict_v01(review[2])),authority_scope_fingerprint=c.digest(dep),
            root_acceptance_state='ACCEPTED_WORK',recording_component='wedding:memory')
        record=address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,safe_summary=c.canonical(value).decode(),semantic_tags=('wedding',kind),
            resonance_reason='Historical bounded context, never current permission.',memory_pointers=(),artifact_pointers=(),source_reference_ids=(source_ref,),lineage_edges=(),time_envelope=env,
            authority_envelope=auth,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),reuse_policy_class='CONTEXT_ONLY',policy_version=POLICY,schema_versions=(POLICY,),
            content_fingerprint=c.digest(material),recording_component='wedding:memory')
        plain=address.meaning_record_to_plain_data_v01(record)
        result=resolver.write_semantic_record(self.drs,resolver.SemanticDRSRecordInput(record_id=record.meaning_record_id,domain=DOMAIN,content=dict(kind=kind,material=material,record=plain),
            semantic_keys=('wedding',kind),time_envelope=dict(pt_created_at=n.stamp(now),kt_asof=n.stamp(now),et_observed_at=n.stamp(now),ct_session_anchor=owner.request_ref,ttl_seconds=3600,freshness_class='static',valid_from=n.stamp(now),valid_to=n.stamp(now+3600)),
            provenance=dict(request_id=owner.request_ref,created_by='root_orchestrator',trace_refs=[dict(trace_id=source_ref)]),root_final_ref=review[2].decision_id,worldstate_ref=c.digest(dep)))
        self.records[record.meaning_record_id]=(record,material)
        self.events.append(dict(op='WRITE',result=result,record=plain,root=n.roots.root_decision_result_to_plain_dict_v01(review[2]),creates_permission=False))
        return record.meaning_record_id

    def select_v01(self,owner,now,kind='accepted_plan'):
        dep=dependencies(owner);root=dep['owner']
        q=resolver.SemanticResolveQuery(query_id=c.identity('memory_query',dict(dependencies=dep,now=now,kind=kind)),domain=DOMAIN,semantic_terms=('wedding',kind),
            content_filters=dict(kind=kind),temporal_query=dict(as_of=n.stamp(now)),worldstate=dep,require_root_review=True)
        report=resolver.resolve_semantic_candidates(self.drs,q,layers=('work',))
        event=dict(op='QUERY',query=asdict(q),report=asdict(report),evaluations=[]);self.events.append(event)
        for candidate in report.candidates:
            pair=self.records.get(candidate.record_id)
            if pair is None:continue
            record,material=pair
            actual=self.drs.read_record('work',candidate.record_id)['content']
            expected=dict(kind=kind,material=material,record=address.meaning_record_to_plain_data_v01(record),
                semantic_keys=['wedding',kind],root_final_ref=record.authority_envelope.source_root_decision_id,
                worldstate_ref=c.digest(material['dependencies']),drs_record_is_truth=False,drs_hit_is_authority=False,
                drs_reuse_candidate_is_action_permission=False)
            c.require(actual==expected,'memory_record_integrity')
            query=memory.build_drs_temporal_query_v01(query_mode='CURRENT_DECISION',semantic_address_id=record.semantic_address.semantic_address_id,scope_fingerprint=c.digest(dep),
                as_of=now,evaluation_time=now,evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',time_range_start=now,time_range_end=now+1,
                required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),freshness_policy_id=record.time_envelope.freshness_policy_id,max_age_seconds=3600,domain=DOMAIN,risk_class='LOW',reuse_intent='CONTEXT',
                requested_reuse_classes=('CONTEXT_ONLY',),required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN','TIME_FITNESS','POLICY_COMPATIBILITY','SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),
                forbidden_changes=('POLICY_CHANGED',),policy_version=POLICY,schema_versions=(POLICY,),owning_local_root_id=root)
            ev=memory.evaluate_drs_candidate_v01(semantic_address=record.semantic_address,query=query,meaning_record=record)
            event['evaluations'].append(memory.query_evaluation_state_to_plain_data_v01(ev))
            if candidate.blocked or not ev.eligible_for_ranking or material['dependencies']!=dep:continue
            budget=memory.build_memory_descent_budget_v01(max_depth=0,max_records_opened=1,max_pointers_opened=0,max_artifacts_opened=0,max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
            plan=memory.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=record.semantic_address.semantic_address_id,proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(),reason_codes=())
            review=n.root_review(root,query.query_id,plan.retrieval_plan_id,record.semantic_address.semantic_address_id,dict(current_dependency=material['dependencies']==dep,eligible=ev.eligible_for_ranking),record.meaning_record_id,
                'wedding:memory:bsep','wedding:memory:topology',now,predicate='approve_controlled_memory_descent_plan_v01',claim_value=memory.retrieval_plan_to_plain_data_v01(plan))
            rh=integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',payload=c.canonical(n.roots.root_decision_result_to_plain_dict_v01(review[2])))
            request=memory.build_memory_descent_request_v01(retrieval_plan_id=plan.retrieval_plan_id,query_id=query.query_id,owning_local_root_id=root,root_kernel_id=review[0].kernel_id,
                root_decision_input_id=review[1].decision_input_id,root_decision_id=review[2].decision_id,root_decision_hash=rh,requested_descent_class='SUMMARY_ONLY',approved_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,
                approved_budget=budget,approved_record_ids=(record.meaning_record_id,),approved_memory_pointer_ids=(),approved_artifact_pointer_ids=())
            result=memory.execute_local_memory_descent_v01(retrieval_plan=plan,proposed_budget=budget,descent_request=request,root_kernel=review[0],root_decision_input=review[1],root_decision_result=review[2],source_records=(record,))
            c.require(result.limits_respected and not result.reason_codes and result.opened_record_ids==(record.meaning_record_id,),'memory_descent')
            event.update(current_query=memory.drs_temporal_query_to_plain_data_v01(query),plan=memory.retrieval_plan_to_plain_data_v01(plan),descent=memory.memory_descent_result_to_plain_data_v01(result),root=n.roots.root_decision_result_to_plain_dict_v01(review[2]))
            return json.loads(result.safe_summaries[0])
        return None
