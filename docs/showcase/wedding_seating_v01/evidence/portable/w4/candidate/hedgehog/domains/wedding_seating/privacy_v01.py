"""Finite trusted projection, not general PII detection or transport authority."""
from dataclasses import dataclass
from .contracts_v01 import (
    CanonicalValueV01, WeddingContractError, array, canonical_bytes_v01, ids,
    keys, opaque, parse_json_v01, parse_problem_v01, require,
)


@dataclass(frozen=True, slots=True)
class DisclosurePolicyV01:
    """Explicit local owner inputs; never populated from a semantic response."""
    profile_ref: str
    structural_disclosure: bool
    guest_ids: tuple
    table_ids: tuple
    condition_ids: tuple
    source_refs: tuple
    safe_intents: tuple

    def __post_init__(self):
        opaque(self.profile_ref)
        require(type(self.structural_disclosure) is bool, 'disclosure_boolean')
        for value in (self.guest_ids, self.table_ids, self.condition_ids, self.source_refs):
            require(type(value) is tuple, 'immutable_policy')
            ids(list(value))
        require(type(self.safe_intents) is tuple and len(self.safe_intents) <= 64, 'immutable_policy')
        refs = []
        for entry in self.safe_intents:
            require(type(entry) is tuple and len(entry) == 2, 'safe_intent_entry')
            refs.append(opaque(entry[0]))
            canonical_bytes_v01(entry[1])
            require(type(entry[1]) is str and bool(entry[1]), 'safe_intent_text')
        ids(refs)


def local_intake_v01(raw, *, expected_source_bundle_hash, expected_source_refs):
    """Separate a known local schema before any external projection is built."""
    value = parse_json_v01(raw)
    keys(value, 'schema_version problem private_registry')
    require(value['schema_version'] == 'WeddingLocalPrivateV01', 'schema_version')
    problem = parse_problem_v01(canonical_bytes_v01(value['problem']),
                               expected_source_bundle_hash=expected_source_bundle_hash,
                               expected_source_refs=expected_source_refs)
    records = array(value['private_registry'], 12, 12)
    for record in records:
        keys(record, 'guest_id name contact private_reason canary')
        opaque(record['guest_id'])
        for key in ('name', 'contact', 'private_reason', 'canary'):
            require(type(record[key]) is str and len(record[key]) <= 1024, 'private_text')
    require(ids([r['guest_id'] for r in records]) == problem.to_plain_v01()['guest_ids'], 'private_guest_binding')
    private = CanonicalValueV01(canonical_bytes_v01({'projection': 'LOCAL_PRIVATE', 'private_registry': records}))
    return problem, private


def resolve_local_intent_v01(text, *, approved_exact_texts):
    """Only exact owner-approved safe strings; unknown text needs local review.

    No name guessing, regex anonymization, LLM redaction or normalization. The
    finite dictionary is local and must not itself be sent to a provider.
    """
    require(type(text) is str and len(text) <= 1024, 'text_bound')
    require(type(approved_exact_texts) is dict and len(approved_exact_texts) <= 64, 'intent_dictionary')
    if text not in approved_exact_texts:
        raise WeddingContractError('NEEDS_LOCAL_REDACTION')
    return opaque(approved_exact_texts[text])


def semantic_projection_v01(problem, role, *, policy):
    require(type(policy) is DisclosurePolicyV01, 'trusted_disclosure_policy')
    require(policy.structural_disclosure, 'STRUCTURAL_DISCLOSURE_DENIED')
    p = problem.to_plain_v01()
    require(p['disclosure_profile_ref'] == policy.profile_ref, 'disclosure_profile_binding')
    require(set(p['guest_ids']) <= set(policy.guest_ids), 'guest_disclosure')
    require({t['table_id'] for t in p['table_records']} <= set(policy.table_ids), 'table_disclosure')
    require({c['condition_id'] for c in p['hard_conditions']} <= set(policy.condition_ids), 'condition_disclosure')
    require({c['source_ref'] for c in p['hard_conditions']} <= set(policy.source_refs), 'source_disclosure')
    safe_intents = dict(policy.safe_intents)
    require(p['safe_intent_ref'] in safe_intents, 'NEEDS_LOCAL_REDACTION')
    require(role in ('ORCHESTRATOR', 'REQUIREMENT_ARCHITECT'), 'semantic_role')
    value = {'projection': 'SEMANTIC_APPROVED', 'synthetic': True, 'role': role,
             'safe_intent': safe_intents[p['safe_intent_ref']]}
    if role == 'ORCHESTRATOR':
        value.update(guest_count=len(p['guest_ids']), table_capacities=[t['capacity'] for t in p['table_records']])
    else:
        value.update(guest_ids=p['guest_ids'], table_records=p['table_records'],
                     hard_conditions=p['hard_conditions'], familiarity_pairs=p['familiarity_pairs'],
                     allowed_objective_profiles=p['allowed_objective_profiles'])
    return CanonicalValueV01(canonical_bytes_v01(value))


def numeric_projection_v01(spec, *, problem, profile, policy):
    from .contracts_v01 import parse_optimization_spec_v01
    require(type(policy) is DisclosurePolicyV01 and policy.structural_disclosure, 'STRUCTURAL_DISCLOSURE_DENIED')
    # Rebuild from the separately supplied original source, not the wire's hash.
    semantic_projection_v01(problem, 'REQUIREMENT_ARCHITECT', policy=policy)
    checked = parse_optimization_spec_v01(spec.canonical, problem=problem, profile=profile).to_plain_v01()
    return CanonicalValueV01(canonical_bytes_v01({
        'projection': 'NUMERIC_APPROVED', 'variable_count': 36,
        'coefficients': checked['qubo_terms'], 'offset': checked['offset'],
    }))


def serialize_approved_projection_v01(supplied, *, independently_expected):
    """Actual serialized bytes are checked, not just a supplied digest.

    The expected value is built by the trusted projection functions above.
    No external write is performed. A match means SERIALIZED_PROJECTION_CHECKED.
    """
    require(type(independently_expected) is CanonicalValueV01, 'expected_projection')
    expected = independently_expected.to_plain_v01()
    require(expected.get('projection') in ('SEMANTIC_APPROVED', 'NUMERIC_APPROVED'), 'external_projection_kind')
    wire = canonical_bytes_v01(supplied)
    require(wire == independently_expected.canonical, 'serialized_projection_mismatch')
    return wire
