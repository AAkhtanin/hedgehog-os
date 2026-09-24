"""Closed W1 contracts. No I/O, SDK, native execution or permission objects.

JSON keys sort lexicographically; unordered ID sets/records are normalized by ID.
Assignments, variable maps and coefficient arrays have semantic order. Integers
are signed 32-bit, never bool. Canonical UTF-8 uses compact ASCII JSON, no newline.
Values own immutable bytes; every plain projection allocates fresh containers.
Content identities establish equality, not truth, currentness or authority.
"""
from dataclasses import dataclass
import hashlib
import json
import re

MAX_BYTES = 256 * 1024
SEMANTIC_BYTES = 32 * 1024
MAX_INT = 2**31 - 1
PROFILES = ('KEEP_FAMILIAR_V01', 'MIX_CIRCLES_V01')
TASKS = ('GENERATE', 'VALIDATE_EXISTING', 'REVISE', 'CLARIFY')
NEEDS = ('ORIGINAL_VALIDATION', 'EXACT_SEARCH', 'REQUIREMENT_REVIEW', 'LOCAL_CLARIFICATION')
OUTPUTS = ('VALIDATION_REPORT', 'SEATING_CANDIDATES', 'CLARIFICATION')
CAPABILITIES = ('VALIDATE_ORIGINAL', 'COMPILE_QUBO', 'SOLVE_EXACT', 'ENCODE_PAIR_10Q')
RESERVED_ORIGINS = ('QPU_RESULT_OBSERVED', 'QPU_ASSISTED_RESULT_ACCEPTED')


class WeddingContractError(ValueError):
    """Stable, bounded local refusal reason; no private material in messages."""


def require(test, reason):
    if not test:
        raise WeddingContractError(reason)


def integer(value, low=0, high=MAX_INT):
    require(type(value) is int and low <= value <= high, 'integer_bound')
    return value


def opaque(value):
    require(type(value) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}', value) is not None, 'opaque_id')
    return value


def digest(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None, 'digest')
    return value


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected.split()), 'closed_keys')


def array(value, maximum, minimum=0):
    require(type(value) is list and minimum <= len(value) <= maximum, 'collection_bound')
    return value


def ids(value, maximum=64, minimum=0):
    array(value, maximum, minimum)
    for item in value:
        opaque(item)
    require(len(set(value)) == len(value), 'duplicate_id')
    return sorted(value)


def _bounded(value, depth=0):
    require(depth <= 16, 'depth_bound')
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        integer(value, -MAX_INT, MAX_INT)
    elif type(value) is str:
        require(len(value) <= 1024 and all(32 <= ord(c) < 127 for c in value), 'text_bound')
    elif type(value) is list:
        require(len(value) <= 34650, 'collection_bound')
        for item in value:
            _bounded(item, depth + 1)
    elif type(value) is dict:
        require(len(value) <= 128, 'collection_bound')
        for key, item in value.items():
            require(type(key) is str, 'key_type')
            _bounded(key, depth + 1)
            _bounded(item, depth + 1)
    else:
        raise WeddingContractError('normative_type')


def canonical_bytes_v01(value, *, limit=MAX_BYTES):
    _bounded(value)
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')
    require(len(raw) <= limit, 'wire_size')
    return raw


def parse_json_v01(raw, *, limit=MAX_BYTES):
    require(type(raw) in (bytes, str), 'wire_type')
    if type(raw) is str:
        require(len(raw) <= limit, 'wire_size')
        raw = raw.encode('utf-8')
    require(len(raw) <= limit, 'wire_size')
    try:
        text = raw.decode('utf-8')
    except UnicodeError as error:
        raise WeddingContractError('utf8') from error
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            require(depth <= 16, 'depth_bound')
        elif char in ']}':
            depth -= 1
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_key')
            result[key] = value
        return result
    def reject(_):
        raise WeddingContractError('normative_float')
    try:
        result = json.loads(text, object_pairs_hook=pairs, parse_float=reject, parse_constant=reject)
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, WeddingContractError):
            raise
        raise WeddingContractError('json_syntax') from error
    _bounded(result)
    return result


def identity_v01(value):
    return hashlib.sha256(canonical_bytes_v01(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class CanonicalValueV01:
    canonical: bytes

    def __post_init__(self):
        require(type(self.canonical) is bytes, 'immutable_bytes')
        require(canonical_bytes_v01(parse_json_v01(self.canonical)) == self.canonical, 'canonical_encoding')

    def to_plain_v01(self):
        return parse_json_v01(self.canonical)

    @property
    def content_id(self):
        return hashlib.sha256(self.canonical).hexdigest()


def _problem(value):
    keys(value, 'schema_version episode_id problem_revision parent_problem_ref owner_root_id guest_ids table_records hard_conditions familiarity_pairs safe_intent_ref source_bundle_hash allowed_objective_profiles disclosure_profile_ref time_context_ref')
    require(value['schema_version'] == 'WeddingProblemV01', 'schema_version')
    for name in ('episode_id', 'owner_root_id', 'safe_intent_ref', 'disclosure_profile_ref', 'time_context_ref'):
        opaque(value[name])
    integer(value['problem_revision'], 1, 1_000_000)
    require((value['parent_problem_ref'] is None) == (value['problem_revision'] == 1), 'parent_revision')
    if value['parent_problem_ref'] is not None:
        digest(value['parent_problem_ref'])
    digest(value['source_bundle_hash'])
    guests = ids(value['guest_ids'], 12, 12)
    tables = array(value['table_records'], 3, 3)
    for table in tables:
        keys(table, 'table_id capacity')
        opaque(table['table_id'])
        integer(table['capacity'], 4, 4)
    tids = ids([t['table_id'] for t in tables], 3, 3)
    conditions = array(value['hard_conditions'], 64)
    for condition in conditions:
        kind = condition.get('predicate') if type(condition) is dict else None
        require(kind in ('TOGETHER', 'APART', 'ALLOWED_TABLES'), 'condition_predicate')
        keys(condition, 'condition_id predicate subjects source_ref hard' + (' tables' if kind == 'ALLOWED_TABLES' else ''))
        opaque(condition['condition_id'])
        opaque(condition['source_ref'])
        require(condition['hard'] is True, 'hard_policy')
        subjects = ids(condition['subjects'], 1 if kind == 'ALLOWED_TABLES' else 2, 1 if kind == 'ALLOWED_TABLES' else 2)
        require(set(subjects) <= set(guests), 'unknown_guest')
        condition['subjects'] = subjects
        if kind == 'ALLOWED_TABLES':
            condition['tables'] = ids(condition['tables'], 3, 1)
            require(set(condition['tables']) <= set(tids), 'unknown_table')
    ids([c['condition_id'] for c in conditions])
    pairs = array(value['familiarity_pairs'], 66)
    for pair in pairs:
        require(ids(pair, 2, 2) == sorted(pair) and set(pair) <= set(guests), 'familiarity_pair')
        pair.sort()
    require(len({tuple(p) for p in pairs}) == len(pairs), 'duplicate_pair')
    profiles = ids(value['allowed_objective_profiles'], 2, 1)
    require(set(profiles) <= set(PROFILES), 'objective_profile')
    value.update(guest_ids=guests, table_records=sorted(tables, key=lambda t: t['table_id']),
                 hard_conditions=sorted(conditions, key=lambda c: c['condition_id']),
                 familiarity_pairs=sorted(pairs), allowed_objective_profiles=profiles)
    return value


@dataclass(frozen=True, slots=True)
class WeddingProblemV01(CanonicalValueV01):
    def __post_init__(self):
        super(WeddingProblemV01, self).__post_init__()
        require(canonical_bytes_v01(_problem(self.to_plain_v01())) == self.canonical, 'problem_order')


def parse_problem_v01(raw, *, expected_source_bundle_hash, expected_source_refs):
    """Expected bindings come from the trusted local intake, never this wire."""
    value = _problem(parse_json_v01(raw))
    require(value['source_bundle_hash'] == digest(expected_source_bundle_hash), 'source_bundle_binding')
    refs = ids(list(expected_source_refs))
    require({c['source_ref'] for c in value['hard_conditions']} <= set(refs), 'condition_source_binding')
    return WeddingProblemV01(canonical_bytes_v01(value))


def mapping_v01(problem):
    p = problem.to_plain_v01()
    return [{'index': 3*g+t, 'guest_id': guest, 'table_id': table['table_id']}
            for g, guest in enumerate(p['guest_ids']) for t, table in enumerate(p['table_records'])]


def binding_v01(problem, profile):
    p = problem.to_plain_v01()
    require(profile in p['allowed_objective_profiles'], 'objective_profile')
    return {'problem_ref': problem.content_id, 'problem_revision': p['problem_revision'],
            'source_bundle_hash': p['source_bundle_hash'], 'owner_root_id': p['owner_root_id'],
            'time_context_ref': p['time_context_ref'], 'objective_profile': profile,
            'mapping_ref': identity_v01(mapping_v01(problem))}


def check_binding_v01(value, problem, profile):
    require(canonical_bytes_v01(value) == canonical_bytes_v01(binding_v01(problem, profile)), 'current_problem_profile_mapping_binding')


@dataclass(frozen=True, slots=True)
class WeddingSemanticProposalV01(CanonicalValueV01):
    pass


def parse_semantic_proposal_v01(raw, *, problem, expected_role, expected_request_ref,
                                expected_actor_ref, expected_model_ref, expected_capture_ref,
                                expected_source_refs):
    value = parse_json_v01(raw, limit=SEMANTIC_BYTES)
    require(expected_role in ('ORCHESTRATOR', 'REQUIREMENT_ARCHITECT'), 'semantic_role')
    common = 'schema_version origin request_ref actor_ref role model_ref capture_ref problem_ref problem_revision source_refs task_kind unresolved reason'
    keys(value, common + (' needs requested_outputs' if expected_role == 'ORCHESTRATOR' else ' objective_profile condition_refs needed_capabilities'))
    require(value['schema_version'] == 'WeddingSemanticProposalV01', 'schema_version')
    require(value['origin'] == 'CONTROLLED_FIXTURE', 'semantic_origin_not_live')
    for key, expected in (('role', expected_role), ('request_ref', expected_request_ref),
                          ('actor_ref', expected_actor_ref), ('model_ref', expected_model_ref),
                          ('capture_ref', expected_capture_ref)):
        opaque(value[key])
        require(value[key] == expected, 'semantic_input_binding')
    p = problem.to_plain_v01()
    require(value['problem_ref'] == problem.content_id and type(value['problem_revision']) is int and value['problem_revision'] == p['problem_revision'], 'semantic_problem_binding')
    value['source_refs'] = ids(value['source_refs'])
    require(set(value['source_refs']) <= set(ids(list(expected_source_refs))), 'semantic_source_binding')
    require(value['task_kind'] in TASKS, 'task_kind')
    value['unresolved'] = ids(value['unresolved'])
    require(type(value['reason']) is str and len(value['reason']) <= 1024, 'reason_bound')
    if expected_role == 'ORCHESTRATOR':
        value['needs'] = ids(value['needs'], len(NEEDS), 1)
        value['requested_outputs'] = ids(value['requested_outputs'], len(OUTPUTS), 1)
        require(set(value['needs']) <= set(NEEDS) and set(value['requested_outputs']) <= set(OUTPUTS), 'need_catalogue')
        if value['task_kind'] == 'VALIDATE_EXISTING':
            require('EXACT_SEARCH' not in value['needs'] and value['requested_outputs'] == ['VALIDATION_REPORT'], 'validate_only_no_search')
        if value['task_kind'] in ('GENERATE', 'REVISE'):
            require({'ORIGINAL_VALIDATION', 'EXACT_SEARCH'} <= set(value['needs']), 'required_need')
    else:
        require(value['objective_profile'] in p['allowed_objective_profiles'] or (value['task_kind'] == 'CLARIFY' and value['objective_profile'] is None), 'objective_profile')
        value['condition_refs'] = ids(value['condition_refs'])
        required = {c['condition_id'] for c in p['hard_conditions']}
        require(set(value['condition_refs']) == required, 'mandatory_condition_refs')
        require({c['source_ref'] for c in p['hard_conditions']} <= set(value['source_refs']), 'mandatory_condition_sources')
        value['needed_capabilities'] = ids(value['needed_capabilities'], len(CAPABILITIES))
        require(set(value['needed_capabilities']) <= set(CAPABILITIES), 'capability_catalogue')
        if value['task_kind'] != 'CLARIFY':
            require('VALIDATE_ORIGINAL' in value['needed_capabilities'], 'mandatory_validation')
        if value['task_kind'] == 'VALIDATE_EXISTING':
            require(value['needed_capabilities'] == ['VALIDATE_ORIGINAL'], 'validate_only_no_search')
    require(value['task_kind'] != 'CLARIFY' or bool(value['unresolved']), 'clarify_evidence')
    return WeddingSemanticProposalV01(canonical_bytes_v01(value, limit=SEMANTIC_BYTES))


@dataclass(frozen=True, slots=True)
class OptimizationSpecV01(CanonicalValueV01):
    pass


@dataclass(frozen=True, slots=True)
class SeatingCandidateSetV01(CanonicalValueV01):
    pass


@dataclass(frozen=True, slots=True)
class SeatingValidationReportV01(CanonicalValueV01):
    pass


def parse_optimization_spec_v01(raw, *, problem, profile):
    from .math_v01 import compile_optimization_v01
    supplied = parse_json_v01(raw)
    expected = compile_optimization_v01(problem, profile).to_plain_v01()
    check_binding_v01(supplied.get('binding'), problem, profile)
    require(canonical_bytes_v01(supplied) == canonical_bytes_v01(expected), 'optimization_exact_derivation')
    return OptimizationSpecV01(canonical_bytes_v01(supplied))


def parse_candidate_set_v01(raw, *, problem, profile, expected_origin, expected_provenance_ref):
    from .math_v01 import ProblemMathV01
    value = parse_json_v01(raw)
    keys(value, 'schema_version binding origin provenance_ref assignments coverage')
    require(value['schema_version'] == 'SeatingCandidateSetV01', 'schema_version')
    check_binding_v01(value['binding'], problem, profile)
    require(value['origin'] in ('LOCAL_EXACT', 'CONTROLLED_FIXTURE') and value['origin'] == expected_origin, 'candidate_origin')
    require(opaque(value['provenance_ref']) == expected_provenance_ref, 'candidate_provenance')
    require(value['coverage'] in ('ALL_BALANCED_PARTITIONS', 'SUPPLIED_ONLY'), 'coverage')
    require(value['origin'] == 'LOCAL_EXACT' or value['coverage'] == 'SUPPLIED_ONLY', 'coverage_origin')
    assignments = array(value['assignments'], 256)
    model = ProblemMathV01(problem)
    for assignment in assignments:
        model.assignment_bits(assignment)
    require(assignments == sorted(assignments) and len({tuple(a) for a in assignments}) == len(assignments), 'candidate_order')
    if value['coverage'] == 'ALL_BALANCED_PARTITIONS':
        require(assignments == [list(a) for a in model.solve(profile)['feasible']], 'candidate_exhaustive_coverage')
    return SeatingCandidateSetV01(canonical_bytes_v01(value))


def parse_validation_report_v01(raw, *, problem, profile, assignment):
    from .math_v01 import validate_assignment_v01
    supplied = parse_json_v01(raw)
    check_binding_v01(supplied.get('binding'), problem, profile)
    expected = validate_assignment_v01(problem, assignment, profile)
    require(canonical_bytes_v01(supplied) == expected.canonical, 'validation_report_derivation')
    return expected
