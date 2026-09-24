"""Trusted owner intake and closed semantic-to-Work requirements for W2."""
from dataclasses import dataclass
import hashlib
import json
from . import contracts_v01 as base, privacy_v01 as privacy
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01

require = base.require
canonical = canonical_json_bytes_v01
def digest(value):
    return hashlib.sha256(value if type(value) is bytes else canonical(value)).hexdigest()
def identity(prefix, value):return prefix+':'+digest(value)

@dataclass(frozen=True)
class OwnerContextV01:
    problem_bytes: bytes
    request_ref: str
    task_kind: str
    profile: str
    approved_intent: str
    parent_ref: str | None = None
    private_tokens: tuple = ()

    def problem(self):
        p=base.parse_json_v01(self.problem_bytes)
        return base.parse_problem_v01(self.problem_bytes,expected_source_bundle_hash=p['source_bundle_hash'],expected_source_refs=source_refs(p))

    def check(self, supplied):
        expected=self.problem()
        p=expected.to_plain_v01()
        value=base.parse_problem_v01(supplied,expected_source_bundle_hash=p['source_bundle_hash'],expected_source_refs=source_refs(p))
        require(value.canonical==expected.canonical,'independent_owner_problem')
        require(self.profile in p['allowed_objective_profiles'] and self.task_kind in base.TASKS,'owner_intent_profile')
        return value


def consume_semantics_v01(owner, supplied_problem, responses, *, policy, serialized_projections):
    require(type(owner) is OwnerContextV01,'owner_context_type')
    problem=owner.check(supplied_problem)
    require(len(responses)==2 and len(serialized_projections)==2,'distinct_roles')
    checked=[]
    require(dict(policy.safe_intents).get(problem.to_plain_v01()['safe_intent_ref'])==owner.approved_intent,'owner_disclosed_intent')
    for i,role in enumerate(('ORCHESTRATOR','REQUIREMENT_ARCHITECT')):
        raw=responses[i].decode() if type(responses[i]) is bytes else responses[i]
        require(not any(token and token in raw for token in owner.private_tokens),'private_semantic_material')
        expected=privacy.semantic_projection_v01(problem,role,policy=policy)
        privacy.serialize_approved_projection_v01(serialized_projections[i],independently_expected=expected)
        value=base.parse_semantic_proposal_v01(responses[i],problem=problem,expected_role=role,
            expected_request_ref=owner.request_ref,expected_actor_ref='actor:'+role,expected_model_ref='model:controlled',
            expected_capture_ref=owner.request_ref+':capture:'+role,expected_source_refs=source_refs(problem.to_plain_v01()))
        require(not any(token and token in canonical(value.to_plain_v01()).decode() for token in owner.private_tokens),'private_semantic_material')
        checked.append(value.to_plain_v01())
    o,a=checked
    require(o['task_kind']==a['task_kind']==owner.task_kind,'cross_role_task')
    require(all(s['source_refs']==list(source_refs(problem.to_plain_v01())) for s in checked),'exact_semantic_sources')
    require(a['objective_profile']==owner.profile,'owner_profile')
    expected={
        'GENERATE':({'REQUIREMENT_REVIEW','EXACT_SEARCH','ORIGINAL_VALIDATION'},{'COMPILE_QUBO','SOLVE_EXACT','VALIDATE_ORIGINAL'}),
        'REVISE':({'REQUIREMENT_REVIEW','EXACT_SEARCH','ORIGINAL_VALIDATION'},{'COMPILE_QUBO','SOLVE_EXACT','VALIDATE_ORIGINAL'}),
        'VALIDATE_EXISTING':({'ORIGINAL_VALIDATION'},{'VALIDATE_ORIGINAL'}),
        'CLARIFY':({'LOCAL_CLARIFICATION'},set()),
    }[owner.task_kind]
    require(set(o['needs'])==expected[0] and set(a['needed_capabilities'])==expected[1],'mandatory_work_set')
    require((owner.task_kind=='CLARIFY')==bool(o['unresolved'] or a['unresolved']),'unresolved_task')
    return dict(problem=problem.to_plain_v01(),profile=owner.profile,task_kind=owner.task_kind,
        request_ref=owner.request_ref,parent_ref=owner.parent_ref,approved_intent=owner.approved_intent,
        semantics=checked,projection_status='SERIALIZED_PROJECTION_CHECKED')


def problem_from_material(material):
    p=material['problem']
    return base.parse_problem_v01(canonical(p),expected_source_bundle_hash=p['source_bundle_hash'],expected_source_refs=source_refs(p))

def source_refs(p):return tuple(sorted({x['source_ref'] for x in p['hard_conditions']}))
