"""Controlled Wedding composition through actual public C/D/Work/Host/Root."""
from dataclasses import dataclass, fields, is_dataclass, replace
from collections.abc import Mapping
import json
import time
from types import SimpleNamespace
from hedgehog import action_commit_packet_v02 as action, work_execution_host_v01 as hosts
from hedgehog.kernel import abi_v01 as abi, work_composition_v01 as w
from . import native_contracts_v01 as c, native_capabilities_v01 as caps, native_adapter_v01 as native, math_v01 as math

def plain(value):
    if type(value) is abi.KernelArtifactV01:return abi.kernel_artifact_to_plain_dict_v01(value)
    if value is None or type(value) in (str,int,float,bool):return value
    if isinstance(value,Mapping):return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [plain(v) for v in value]
    if is_dataclass(value):return {f.name:plain(getattr(value,f.name)) for f in fields(value)}
    raise TypeError(type(value).__name__)

class ControlledSourceV01:
    def __init__(self,now,clock_origin='wedding.controlled_clock'):
        self.reads=0
        self.snapshot=hosts.TrustedWorkSourceSnapshotV01((),action.build_logical_time_bridge_v01(
            origin_utc_epoch_seconds=now,seconds_per_tick=1,bridge_policy_version='wedding.controlled.v01'),
            now,clock_origin,'wedding:current',0)
    def read_current_v01(self):
        self.reads+=1
        return self.snapshot

@dataclass
class NativeRunV01:
    owner: object
    material: dict
    common: dict
    program: object
    host: object
    source: object
    outcome: object
    reviews: tuple
    final_review: tuple
    output: dict
    evidence: dict

    def validate_current(self,owner):
        c.require(owner==self.owner,'current_owner_context')
        current=self.source.read_current_v01()
        c.require(current==self.host.current_sources and plain(current)==self.evidence['trusted_source'],'current_source_snapshot')
        c.require(current.evaluation_time==self.evidence['now'],'current_source_time')
        ctx=w.work_continuation_context_v01(self.host,task_id=self.program.candidate.task_id,expected_revision=self.host.state_revision)
        ok,reasons=w.validate_work_program_result_v01(self.program,self.outcome.results,**self.common,
            host_map={self.host.owning_root_id:self.host},review_bindings=self.reviews,continuation_context=ctx)
        c.require(ok,'supplied_work:'+repr(reasons))
        expected=caps.material(self.outcome.results[-1].result.output)['safe_output']
        c.require(expected==self.output,'actual_consumed_output')
        c.require(self.evidence['host_revision']==self.host.state_revision,'current_host_revision')
        c.require(self.final_review[2].selected_candidate_id==c.identity('wedding_result',self.output),'current_root_output')
        c.require(not native.roots.validate_root_decision_result_v01(kernel=self.final_review[0],decision_input=self.final_review[1],result=self.final_review[2]),'root_supplied')
        return True


def execute_v01(owner,supplied_problem,responses,*,policy,serialized_projections,now,existing=None,journal=lambda *a,**k:None):
    material=c.consume_semantics_v01(owner,supplied_problem,responses,policy=policy,serialized_projections=serialized_projections)
    return _execute_material_v01(owner,material,now=now,existing=existing,journal=journal)


def _execute_material_v01(owner,material,*,now,existing=None,journal=lambda *a,**k:None):
    """Shared native producer; callers first validate their own ingress lane."""
    witness=math.contradiction_witness_v01(owner.problem())
    if witness:return dict(status='UNSAT_SUPPORTED_DIRECT_PAIR',condition_witness=witness,search_calls=0,material=material)
    if owner.task_kind=='CLARIFY':
        from .qpu_contracts_v01 import clarification_v01
        unresolved=sorted(set(x for s in material['semantics'] for x in s['unresolved']))
        return dict(status='NEEDS_CLARIFICATION',**clarification_v01(unresolved),search_calls=0,material=material)
    if owner.task_kind=='VALIDATE_EXISTING':
        c.require(type(existing) is NativeRunV01,'actual_existing_run_required')
        existing.validate_current(existing.owner)
        c.require(existing.owner.problem().canonical==owner.problem().canonical,'existing_original_problem')
        material.update(assignment=list(existing.output['assignment']),existing_result_ref=existing.evidence['artifact']['artifact_id'])
    root=material['problem']['owner_root_id'];task=owner.request_ref;host_ref='host:'+task
    catalogue=caps.catalogue_v01(host_ref)
    clock_origin='wedding.wall_clock_snapshot' if owner.task_kind in ('QPU_PREPARE','QPU_CONSUME') else 'wedding.controlled_clock'
    source,intake_review=native.semantic_source(owner.approved_intent,task,root,now,material['semantics'][0],clock_origin=clock_origin)
    proposal=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('wedding_semantics',material),artifact_type='SemanticArchitectProposal',
        schema_version='v1',transaction_id='transaction:'+task,owner_root_id=root,source_component='semantic_architect',authority_class='ADVISORY',
        lifecycle_state='PROPOSED',payload=material,trace_refs=('intent:'+task,),parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope=dict(pt_created_at=native.stamp(now),kt_asof=native.stamp(now),et_observed_at=None,ct_session_anchor=task,
            ttl_seconds=3600,freshness_class='static',valid_from=native.stamp(now),valid_to=native.stamp(now+3600)))
    common=dict(catalogue=catalogue,source_context=source,semantic_proposal=proposal)
    names=('review','compile','solve','validate','consume') if owner.task_kind in ('GENERATE','REVISE') else ('validate','consume')
    if owner.task_kind=='QPU_PREPARE':names=('review','compile','qpu_prepare')
    elif owner.task_kind=='QPU_CONSUME':names=('qpu_validate','qpu_consume')
    definitions={x.definition.operation_id:x.definition.definition_id for x in catalogue}
    items=[]
    for i,name in enumerate(names):
        binding=w.WorkLiteralV01(caps.record(material)[0]) if i==0 else w.WorkOutputBindingV01(names[i-1],'material','TEXT')
        items.append(w.WorkItemV01(name,definitions['wedding.'+name],root,(w.WorkInputBindingV01('material',binding),),(),() if i==0 else (names[i-1],),None,None))
    review_ceiling=native.d.build_fractal_runtime_policy_v02(required_downstream_capability_ids=(),permitted_child_scope_refs=()).max_total_cells-1
    params=dict(task_id=task,previous_revision_id=None,intent_ref='intent:'+task,bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,
        catalogue_revision=0,budget=w.WorkBudgetV01(len(items),review_ceiling,0,len(items),0),items=tuple(items),trigger_evidence_refs=())
    candidate=w.build_work_program_candidate_v01(**params,**common)
    journal('C_ROUTE_START',task=task)
    ds,common=native.source_family(SimpleNamespace(id=task,root=root),common,items[-1],candidate,now)
    candidate=w.build_work_program_candidate_v01(**params,**common)
    obligation=w.build_work_review_obligation_v01(candidate=candidate,item=items[-1],source_context=ds)
    items[-1]=replace(items[-1],review_obligation_id=obligation.obligation_id)
    candidate=w.build_work_program_candidate_v01(**dict(params,items=tuple(items)),**common)
    program=w.materialize_work_program_v01(candidate,**common)
    obligation=w.build_work_review_obligation_v01(candidate=candidate,item=items[-1],source_context=ds)
    original_policy=w.build_work_task_policy_v01(candidate,**common,host_instance_ref=host_ref,definition_ids=tuple(sorted(definitions.values())),resource_refs=())
    trusted=ControlledSourceV01(now,clock_origin)
    host=hosts.build_root_work_execution_host_v01(owning_root_id=root,registry=action.build_empty_action_commit_packet_registry_v02(),catalogue=catalogue,
        packet_bindings=(),current_dependency_observations=(),logical_time_bridge=trusted.snapshot.logical_time_bridge,trusted_source=trusted,task_policies=(original_policy,))
    ctx=w.enroll_work_program_v01(host,program,**common,expected_revision=host.state_revision)
    journal('D_REVIEW_START',task=task);start=time.monotonic()
    review=w.execute_work_task_review_v01(ctx,obligation=obligation,source_context=ds,semantic_proposal=proposal)
    elapsed=time.monotonic()-start;journal('D_REVIEW_RETURN',task=task,seconds=elapsed)
    c.require(type(review) is tuple,'native_review_incomplete:'+str(getattr(review,'reason',None)))
    ctx=w.work_continuation_context_v01(host,task_id=task,expected_revision=host.state_revision)
    journal('WORK_START',task=task)
    outcome=w.advance_work_program_v01(program,**common,host_map={root:host},review_bindings=(review,),continuation_context=ctx)
    c.require(all(r.status=='COMPLETED' for r in outcome.results) and len(outcome.results)==len(items),'work_incomplete')
    final=caps.material(outcome.results[-1].result.output);output=final['safe_output']
    c.require(trusted.read_current_v01()==host.current_sources and trusted.snapshot.evaluation_time==now,'before_root_current_source')
    if owner.task_kind=='QPU_PREPARE':
        from . import qpu_contracts_v01 as q
        original_valid=output==q.numeric_v01(final)
    else:original_valid=final['validation']==math.validate_assignment_v01(owner.problem(),output['assignment'],owner.profile).to_plain_v01()
    checks=dict(original_valid=original_valid,
        original_source=final['problem']==owner.problem().to_plain_v01(),current_profile=output['profile']==owner.profile,current_request=output['request_ref']==task)
    ctx=w.work_continuation_context_v01(host,task_id=task,expected_revision=host.state_revision)
    artifact=w.work_program_result_to_artifact_v01(program,outcome.results,**common,host_map={root:host},review_bindings=(review,),continuation_context=ctx)
    decision=native.root_review(root,'transaction:'+task,c.identity('wedding_result',output),task,checks,artifact.artifact_id,
        candidate.bsep_ref,program.topology_artifact.artifact_id,now,predicate='wedding_current_safe_output',claim_value=output)
    evidence=dict(now=now,owner=dict(problem=owner.problem().to_plain_v01(),request_ref=task,task_kind=owner.task_kind,profile=owner.profile,parent_ref=owner.parent_ref),
        material=material,program=plain(program),policy=plain(original_policy),results=plain(outcome.results),artifact=plain(artifact),
        source_context=plain(common['source_context']),semantic_proposal=plain(proposal),D_source=plain(ds),D_report=plain(review[2].runtime_report),
        D_bundle=plain(review[2]),review_obligation=plain(obligation),trusted_source=plain(host.current_sources),
        D_seconds=elapsed,output=output,root_input=plain(decision[1]),root_result=plain(decision[2]),
        task_snapshot=plain(w.inspect_work_task_v01(host,task_id=task)),host_revision=host.state_revision,events=plain(host.events),
        counters=dict(native_tasks=1,native_dispatches=len(items),llm=0,aws=0,qpu=0,effects=0),
        classification=material.get('origin','CONTROLLED_NATIVE_SEMANTIC_CONSUMPTION'))
    result=NativeRunV01(owner,material,common,program,host,trusted,outcome,(review,),decision,output,evidence)
    result.validate_current(owner);journal('WORK_ROOT_COMPLETE',task=task)
    return result
