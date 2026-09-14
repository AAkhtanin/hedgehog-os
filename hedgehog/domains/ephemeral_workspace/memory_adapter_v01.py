"""Local DRS semantic candidates, current Root descent and no retained permissions."""
from dataclasses import asdict
from datetime import datetime,timezone
import json
from pathlib import Path
from hedgehog.drs import LocalDRS
from hedgehog import local_drs_resolver as resolver
from hedgehog import drs_semantic_address_v01 as address, drs_memory_resolution_v01 as memory
from hedgehog.kernel import integrity_replay_v01 as integrity
from . import contracts_v01 as c, kernel_adapter_v01 as kernel, semantic_roles_v01 as roles

POLICY='ews.semantic_recipe.v01'
DOMAIN='EPHEMERAL_WORKSPACE'


def stamp(now):
    return datetime.fromtimestamp(now,timezone.utc).isoformat()


def dependencies(session):
    return dict(assets=sorted(session.source_hashes.values()),
        media=None if session.media_fixture is None else c.digest(session.media_fixture['manifest']),
        classes=sorted(c.CLASSES),policy=POLICY)


def _review(root,material,now,predicate='ews_semantic_memory_writeback'):
    ref=c.identity('memory_material',material)
    return kernel.root_review(root,'transaction:'+ref,ref,'ews:semantic_memory',
        dict(finite_content=len(c.canonical(material))<16384,no_effect_grant=True),ref,'ews:memory:bsep','ews:memory:topology',now,
        predicate=predicate,claim_value=material)


def _record(material,review,now,ttl,root):
    addr=address.build_semantic_address_v01(namespace='ews',domain=DOMAIN,subject_class=material['kind'],
        intent_class='context_lookup',meaning_schema_id='ews.semantic_recipe',meaning_schema_version='v0.1')
    env=address.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=now,ct_context_anchor=now,
        ttl_seconds=ttl,valid_from=now,valid_to=now+ttl,source_observed_at=now,source_reported_at=now,
        system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:ews:recipe')
    auth=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=root,
        source_root_decision_input_id=review[1].decision_input_id,source_root_decision_id=review[2].decision_id,
        source_root_decision_hash=c.digest(kernel.roots.root_decision_result_to_plain_dict_v01(review[2])),
        authority_scope_fingerprint=c.digest(material['dependencies']),root_acceptance_state='ACCEPTED_WORK',recording_component='ews:memory')
    summary_value=material['value'] if material['kind']=='semantic_recipe' else material['value']['selection']
    summary=c.canonical(summary_value).decode()
    c.require(len(summary)<=1024,'semantic_memory_summary_bound')
    return address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
        safe_summary=summary,semantic_tags=('workspace',),resonance_reason='Bounded semantic content, fresh review required.',
        memory_pointers=(),artifact_pointers=(),source_reference_ids=tuple(
            c.digest(ref.encode()) if material['kind']=='semantic_recipe' else ref for ref in material['sources']),lineage_edges=(),time_envelope=env,
        authority_envelope=auth,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),reuse_policy_class='CONTEXT_ONLY',
        policy_version=POLICY,schema_versions=(POLICY,),content_fingerprint=c.digest(material),recording_component='ews:memory')


class SemanticMemory:
    def __init__(self,directory):
        self.drs=LocalDRS(Path(directory))
        self.events=[]

    def _write(self,session,kind,value,sources,ttl):
        c.require(type(ttl) is int and 0<ttl<=86400,'memory_finite_validity')
        session.current()
        now=session.source.sample().evaluation_time
        material=dict(kind=kind,request=session.request,dependencies=dependencies(session),value=value,sources=sources)
        review=_review(session.root,material,now)
        record=_record(material,review,now,ttl,session.root)
        plain=address.meaning_record_to_plain_data_v01(record)
        result=resolver.write_semantic_record(self.drs,resolver.SemanticDRSRecordInput(record_id=record.meaning_record_id,
            domain=DOMAIN,content=dict(kind=kind,request=session.request,worldstate=dependencies(session),material=material,
                record=plain,root_result=kernel.roots.root_decision_result_to_plain_dict_v01(review[2])),
            semantic_keys=('workspace',kind),time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=stamp(now),
                ct_session_anchor=session.id,ttl_seconds=ttl,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+ttl)),
            provenance=dict(request_id=session.id,created_by='root_orchestrator',trace_refs=[dict(trace_id=sources[0])]),
            root_final_ref=review[2].decision_id,worldstate_ref=c.digest(material['dependencies'])))
        self.events.append(dict(op='WRITE',record=result,root_input=kernel.roots.root_decision_input_to_plain_dict_v01(review[1]),
            records_written=1,storage='EXPLICIT_DURABLE_LOCAL_DRS',creates_permission=False))
        return record.meaning_record_id

    def remember(self,session,ttl=3600):
        c.require(session.work_results and session.semantic_responses==[x['output'] for x in session.captures],'memory_actual_semantic_work')
        return self._write(session,'semantic_recipe',session.semantic_responses,
            [x['response_ref'] for x in session.captures]+[session.work_artifact.artifact_id],ttl)

    def remember_saved(self,session,ttl=86400):
        c.require(session.saved is not None,'memory_no_saved_work')
        file=session.directory/'output/selection.json'
        data=file.read_bytes();c.require(c.digest(data)==session.saved['sha256'],'memory_sidecar_binding')
        sidecar=json.loads(data)
        selection=[{k:item[k] for k in ('asset','rating','selected','exposure','crop')} for item in sidecar['selection']]
        # Summary-only descent exposes the useful selection, not opaque handles.
        value=dict(sidecar_sha256=c.digest(data),selection=selection,history_ref=c.digest(session.history))
        return self._write(session,'saved_work',value,[session.saved['sha256'],c.digest(session.history)],ttl)

    def select(self,*,root,request,dependency,now,kind='semantic_recipe',policy=POLICY):
        query=resolver.SemanticResolveQuery(query_id=c.identity('memory_search',dict(root=root,request=request,dependency=dependency,now=now,kind=kind)),
            domain=DOMAIN,semantic_terms=('workspace',kind),content_filters=dict(kind=kind,request=request),
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
                policy_version=policy,schema_versions=(POLICY,),owning_local_root_id=root)
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
                'ews:memory:bsep','ews:memory:topology',now,predicate='approve_controlled_memory_descent_plan_v01',
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
            if kind=='saved_work':
                selected=dict(selection=selected,sidecar_sha256=record.source_reference_ids[0],history_ref=record.source_reference_ids[1])
            return selected,dict(record_id=record.meaning_record_id,descent_id=result.memory_descent_result_id)
        return None


class MemoryProvider:
    mode='DRS_REUSE_CANDIDATE'
    model='local-drs-semantic-candidate-v01'
    def __init__(self,store):
        self.store=store;self.calls=0

    def prepare(self,session):
        selected=self.store.select(root=session.root,request=session.request,dependency=dependencies(session),now=session.source.sample().evaluation_time)
        c.require(selected is not None,'memory_no_eligible_recipe')
        self.responses,self.origin=selected

    def respond(self,role,context):
        # All three role-specific contracts and fresh route review still run.
        return roles.validate(role,json.loads(c.canonical(self.responses[roles.ROLES.index(role)])),context)
