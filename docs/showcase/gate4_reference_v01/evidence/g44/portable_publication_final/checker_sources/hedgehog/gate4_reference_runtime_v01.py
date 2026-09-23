"""Serial G42 allocation consumption through the unchanged enrolled Work API.

This consumer checks a finite application-owned work inventory. It does not
grant action authority or bypass the Host's independent cumulative accounting.
"""
from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
import time

from hedgehog import action_commit_packet_v02 as actions
from hedgehog.kernel import abi_v01 as abi, work_composition_v01 as work, root_decision_v01 as roots
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from hedgehog.gate4_reference_contracts_v01 import ReferenceValueV01, require
from hedgehog.gate4_pressure_budget_v01 import validate_reference_allocation_v01


def plain_v01(value):
    if type(value) is abi.KernelArtifactV01:
        return abi.kernel_artifact_to_plain_dict_v01(value)
    if type(value) is roots.RootDecisionInputV01: return roots.root_decision_input_to_plain_dict_v01(value)
    if type(value) is roots.RootDecisionKernelV01: return roots.root_decision_kernel_to_plain_dict_v01(value)
    if type(value) is roots.RootDecisionResultV01: return roots.root_decision_result_to_plain_dict_v01(value)
    if value is None or type(value) in (str,int,bool,float): return value
    if type(value) in (tuple,list): return [plain_v01(v) for v in value]
    if type(value) is dict: return {k:plain_v01(v) for k,v in value.items()}
    require(is_dataclass(value) and not isinstance(value,type),'native_plain_type')
    return {f.name:plain_v01(getattr(value,f.name)) for f in fields(value)}


def canonical_v01(value): return canonical_json_bytes_v01(plain_v01(value))
def digest_v01(value): return hashlib.sha256(canonical_v01(value)).hexdigest()
def local_id_v01(kind,value): return 'g4_reference:'+kind+':'+hashlib.sha256(str(value).encode()).hexdigest()
def literal_v01(name,value):
    return work.WorkInputBindingV01(name,work.WorkLiteralV01(actions.ActionEffectParameterRecordV01(name,'TEXT',canonical_v01(value).decode())))


class TaskClockV43:
    """Trusted harness clock installed before enrollment, never read from reports."""
    def __init__(self, controlled_time=None):
        require(controlled_time is None or type(controlled_time) is int,'native_clock_type')
        self._controlled=controlled_time
        self._last=None
        self._task=None

    def bind_v01(self, task):
        require(self._task is None,'native_clock_already_bound')
        self._task=task

    def now_v01(self, task=None):
        require(task is None or self._task==task,'native_clock_task')
        now=int(time.time()) if self._controlled is None else self._controlled
        require(self._last is None or now>=self._last,'native_clock_rollback')
        self._last=now
        return now

    def advance_v01(self, now):
        require(self._controlled is not None and type(now) is int and now>=self._controlled,'native_clock_advance')
        self._controlled=now


@dataclass(frozen=True)
class NativeWorkInventoryV01:
    """Trusted application construction, not a serialized public trust flag."""
    branches: tuple
    final_definition_id: str
    final_material: bytes
    final_work_id: str = 'final_strategy'


class NativeAllocationConsumerV01:
    def __init__(self, *, host, task_id, common, inventory, budget, trigger, original_basis, history_store, task_clock):
        from hedgehog.domains.airline.gate4_reference_adapter_v01 import reconstruct_allocation_basis_v43, derive_budget_from_originals_v43
        require(type(inventory) is NativeWorkInventoryV01,'native_inventory_type')
        require(type(task_clock) is TaskClockV43,'native_clock_type')
        self.task_clock=task_clock
        self.history_store=history_store
        expected_basis=reconstruct_allocation_basis_v43(host=host,task_id=task_id,common=common,
            history_store=history_store,task_clock=task_clock)
        require(canonical_v01(original_basis)==canonical_v01(expected_basis),'native_original_basis_substitution')
        expected_budget=derive_budget_from_originals_v43(expected_basis,common['semantic_proposal'],json.loads(inventory.final_material))
        require(ReferenceValueV01('budget',budget)==ReferenceValueV01('budget',expected_budget),'native_source_derived_budget')
        self.host=host; self.task_id=task_id; self.common=common; self.inventory=inventory
        self.budget=ReferenceValueV01('budget',budget)
        self.snapshot=work.inspect_work_task_v01(host,task_id=task_id)
        self.clock=canonical_v01(host.current_sources)
        self.original_basis=canonical_v01(original_basis)
        self.history_head=canonical_v01(history_store.head_v01())
        self.trigger=trigger
        policy=self.snapshot.policy
        proposal=plain_v01(common['semantic_proposal'])
        need=proposal['payload']
        for key,value in dict(policy=plain_v01(policy),usage=plain_v01(self.snapshot),source=plain_v01(common['source_context']),
                time_envelope=proposal['time_envelope'],domain=need['domain'],configuration=need['finite_catalogue'],
                utility_profile=need['utility_profile'],history=need['history']).items():
            require(canonical_v01(original_basis[key])==canonical_v01(value),'native_enrolled_source_need:'+key)
        require(work.validate_installed_work_task_policy_v01(policy,owning_root_id=host.owning_root_id,catalogue=common['catalogue']),'native_original_policy')
        require(policy.task_id==task_id and policy.max_compute_units==budget['total'] and self.snapshot.usage.compute_units==budget['spent']
                and self.snapshot.host_revision==budget['host_revision'],'native_budget_binding')
        binding=budget['context']['native_binding']
        require(binding['original_policy_sha256']==digest_v01(policy) and binding['original_usage_sha256']==digest_v01(self.snapshot)
                and binding['basis_sha256']==hashlib.sha256(self.original_basis).hexdigest(),'native_original_projection_binding')
        require(inventory.final_definition_id in policy.definition_ids,'native_final_definition')
        rows=budget['mandatory']; require(len(rows)==1 and rows[0]['kind']=='FINAL_CONSUMER' and rows[0]['count']==1,'native_mandatory_consumer')
        require(rows[0]['definition_ref']==local_id_v01('definition',inventory.final_definition_id)
                and rows[0]['material_sha256']==hashlib.sha256(inventory.final_material).hexdigest(),'native_mandatory_material')
        ids=[b for b,_ in inventory.branches]
        require(len(set(ids))==len(ids) and set(ids)=={b['id'] for b in budget['pressure_inputs']['branches']},'native_branch_inventory')
        all_items=[i for _,items in inventory.branches for i in items]
        require(len({i.work_id for i in all_items})==len(all_items) and all(i.definition_id in policy.definition_ids and i.owning_root_id==host.owning_root_id for i in all_items),'native_inventory_scope')
        manifest=[]
        for branch,items in inventory.branches:
            for ordinal,item in enumerate(items,1):
                require(len(item.inputs)==1 and item.inputs[0].input_field=='material' and type(item.inputs[0].source) is work.WorkLiteralV01,'native_quantum_literal')
                raw=item.inputs[0].source.value.value.encode()
                manifest.append(dict(branch=branch,ordinal=ordinal,work_id=item.work_id,definition_id=item.definition_id,material_sha256=hashlib.sha256(raw).hexdigest()))
        require(manifest==need['allowed_quantum_manifest'],'native_enrolled_inventory')

    def expected_items_v01(self, supplied):
        budget=self.budget.plain()
        value=validate_reference_allocation_v01(supplied,inputs=budget['pressure_inputs'],current_budget_context=budget).plain()
        require(value['status']=='ALLOCATED','native_allocation_not_ready')
        counts={r['id']:r['allocation'] for r in value['rows']}
        selected=[]
        for branch,items in self.inventory.branches:
            count=counts.get(branch,0)
            require(count<=len(items),'native_quota_catalogue')
            selected.extend(items[:count])
        proof=dict(profile='G43_ALLOCATION_WORK_PROOF_V01',basis=json.loads(self.original_basis),
            proposal=plain_v01(self.common['semantic_proposal']),budget=budget,allocation=value)
        bindings=[literal_v01('material',json.loads(self.inventory.final_material)),literal_v01('allocation_proof',proof),work.WorkInputBindingV01('previous',self.trigger.output)]
        for index,item in enumerate(selected):
            bindings.append(work.WorkInputBindingV01('q'+str(index),work.WorkOutputBindingV01(item.work_id,'material','TEXT')))
        final=work.WorkItemV01(self.inventory.final_work_id,self.inventory.final_definition_id,self.host.owning_root_id,
            tuple(bindings),(),tuple(i.work_id for i in selected),None,None)
        return tuple(selected)+(final,)

    def validate_v01(self, supplied, *, proposed_items, current_budget_context, original_basis):
        from hedgehog.domains.airline.gate4_reference_adapter_v01 import validate_current_basis_v43
        validate_current_basis_v43(json.loads(self.original_basis),self.task_clock.now_v01(self.task_id))
        require(canonical_v01(self.history_store.head_v01())==self.history_head,'native_history_head_changed')
        history=json.loads(self.original_basis)['history'].get('bridge')
        if history is not None:
            from datetime import datetime
            require(self.task_clock.now_v01(self.task_id)<int(datetime.fromisoformat(history['time_envelope']['valid_to']).timestamp()),'native_current_history_expired')
        require(work.inspect_work_task_v01(self.host,task_id=self.task_id)==self.snapshot,'native_stale_usage_revision')
        require(canonical_v01(self.host.current_sources)==self.clock,'native_current_source_changed')
        require(canonical_v01(original_basis)==self.original_basis,'native_independent_basis_changed')
        require(ReferenceValueV01('budget',current_budget_context)==self.budget,'native_budget_substitution')
        expected=self.expected_items_v01(supplied)
        require(type(proposed_items) is tuple and proposed_items==expected,'native_unapproved_work_set')
        require(sum(r['allocation'] for r in ReferenceValueV01('allocation_report',supplied).plain()['rows'])+1==len(expected),'native_unit_mapping')
        context=work.work_continuation_context_v01(self.host,task_id=self.task_id,expected_revision=self.snapshot.host_revision)
        valid,reasons=work.validate_work_revision_trigger_v01(self.trigger,context=context)
        require(valid,'native_historical_trigger:'+repr(reasons))
        return context

    def install_v01(self, supplied, *, proposed_items, current_budget_context, original_basis):
        context=self.validate_v01(supplied,proposed_items=proposed_items,current_budget_context=current_budget_context,original_basis=original_basis)
        remaining=self.snapshot.policy.max_compute_units-self.snapshot.usage.compute_units
        budget=work.WorkBudgetV01(self.snapshot.policy.max_items,0,0,remaining,
            self.snapshot.policy.max_revisions-self.snapshot.usage.revisions-1)
        return work.revise_work_program_v01(context,previous_revision_id=self.snapshot.current_revision_id,
            trigger=self.trigger,items=proposed_items,budget=budget,**self.common)
