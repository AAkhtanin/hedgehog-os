"""Exact original 12-guest mathematics; stdlib only, no provider or native work.

H is a sum of nonnegative integer penalties and vanishes iff the original
conditions hold. On feasible assignments KEEP <= 2*len(familiarity), MIX <=
len(familiarity). The penalty bound+1 strictly separates invalid from feasible
states, provided a feasible state exists. This is not a hardware-success proof.
"""
from dataclasses import dataclass
from itertools import combinations
from .contracts_v01 import (
    OptimizationSpecV01, SeatingCandidateSetV01, SeatingValidationReportV01,
    WeddingProblemV01, array, binding_v01, canonical_bytes_v01, integer,
    mapping_v01, require,
)


@dataclass(frozen=True, slots=True, init=False)
class ProblemMathV01:
    problem: WeddingProblemV01
    guests: tuple
    tables: tuple
    conditions: tuple
    familiar: tuple

    def __init__(self, problem):
        require(type(problem) is WeddingProblemV01, 'problem_type')
        p = problem.to_plain_v01()
        guests = tuple(p['guest_ids'])
        tables = tuple(t['table_id'] for t in p['table_records'])
        conditions = tuple((c['condition_id'], c['predicate'], tuple(guests.index(g) for g in c['subjects']),
                            tuple(tables.index(t) for t in c.get('tables', [])), c['source_ref']) for c in p['hard_conditions'])
        for name, value in (('problem', problem), ('guests', guests), ('tables', tables),
                            ('conditions', conditions), ('familiar', tuple(tuple(guests.index(g) for g in pair) for pair in p['familiarity_pairs']))):
            object.__setattr__(self, name, value)

    def penalty(self, profile):
        require(profile in self.problem.to_plain_v01()['allowed_objective_profiles'], 'objective_profile')
        return (2 if profile == 'KEEP_FAMILIAR_V01' else 1)*len(self.familiar) + 1

    def assignment_bits(self, assignment):
        require(type(assignment) in (list, tuple) and len(assignment) == 12, 'assignment_shape')
        for table in assignment:
            integer(table, 0, 2)
        return tuple(int(assignment[g] == t) for g in range(12) for t in range(3))

    def components(self, bits):
        require(type(bits) in (tuple, list) and len(bits) == 36, 'bits_shape')
        for bit in bits:
            integer(bit, 0, 1)
        hard = sum((sum(bits[3*g:3*g+3])-1)**2 for g in range(12))
        hard += sum((sum(bits[3*g+t] for g in range(12))-4)**2 for t in range(3))
        for _, kind, subjects, allowed, _ in self.conditions:
            g = subjects[0]
            if kind == 'TOGETHER':
                hard += sum((bits[3*g+t]-bits[3*subjects[1]+t])**2 for t in range(3))
            elif kind == 'APART':
                hard += sum(bits[3*g+t]*bits[3*subjects[1]+t] for t in range(3))
            else:
                hard += sum(bits[3*g+t] for t in range(3) if t not in allowed)
        keep = sum((bits[3*g+t]-bits[3*h+t])**2 for g, h in self.familiar for t in range(3))
        mix = sum(bits[3*g+t]*bits[3*h+t] for g, h in self.familiar for t in range(3))
        return hard, keep, mix

    def verdicts(self, assignment):
        self.assignment_bits(assignment)
        verdicts = [{'condition_id': 'builtin:capacity:' + table, 'source_ref': 'original:table_records',
                     'satisfied': assignment.count(t) == 4} for t, table in enumerate(self.tables)]
        for cid, kind, subjects, allowed, source in self.conditions:
            g = subjects[0]
            if kind == 'TOGETHER':
                result = assignment[g] == assignment[subjects[1]]
            elif kind == 'APART':
                result = assignment[g] != assignment[subjects[1]]
            else:
                result = assignment[g] in allowed
            verdicts.append({'condition_id': cid, 'source_ref': source, 'satisfied': result})
        return verdicts

    def balanced_assignments(self):
        for first in combinations(range(12), 4):
            remaining = tuple(g for g in range(12) if g not in first)
            for second in combinations(remaining, 4):
                yield tuple(0 if g in first else 1 if g in second else 2 for g in range(12))

    def solve(self, profile):
        self.penalty(profile)
        return self.solve_profiles()[profile]

    def solve_profiles(self):
        feasible = []
        evaluated = 0
        for assignment in self.balanced_assignments():
            evaluated += 1
            if all(v['satisfied'] for v in self.verdicts(assignment)):
                feasible.append(assignment)
        feasible.sort()
        result = {}
        for profile in self.problem.to_plain_v01()['allowed_objective_profiles']:
            scores = {a: (2*sum(a[g] != a[h] for g, h in self.familiar) if profile == 'KEEP_FAMILIAR_V01'
                          else sum(a[g] == a[h] for g, h in self.familiar)) for a in feasible}
            optimum = min(scores.values()) if scores else None
            tied = [a for a in feasible if scores[a] == optimum]
            result[profile] = {'status': 'FEASIBLE' if feasible else 'UNSAT_SUPPORTED', 'evaluated': evaluated,
                               'feasible': feasible, 'optimum': optimum, 'tied_optima': tied,
                               'selected': tied[0] if tied else None,
                               'witness': contradiction_witness_v01(self.problem) if not feasible else []}
        return result


def contradiction_witness_v01(problem):
    conditions = problem.to_plain_v01()['hard_conditions']
    for a in conditions:
        if a['predicate'] != 'TOGETHER':
            continue
        for b in conditions:
            if b['predicate'] == 'APART' and a['subjects'] == b['subjects']:
                return [{'condition_id': c['condition_id'], 'source_ref': c['source_ref']} for c in (a, b)]
    return []


def compile_optimization_v01(problem, profile):
    model = ProblemMathV01(problem)
    penalty = model.penalty(profile)
    terms, offset = {}, 0
    def add(i, j, coefficient):
        key = tuple(sorted((i, j)))
        terms[key] = terms.get(key, 0) + coefficient
    def square(indices, target, weight):
        nonlocal offset
        offset += weight*target*target
        for i in indices:
            add(i, i, weight*(1-2*target))
        for i, j in combinations(indices, 2):
            add(i, j, 2*weight)
    def difference(i, j, weight):
        add(i, i, weight)
        add(j, j, weight)
        add(i, j, -2*weight)
    for g in range(12):
        square(tuple(3*g+t for t in range(3)), 1, penalty)
    for t in range(3):
        square(tuple(3*g+t for g in range(12)), 4, penalty)
    for _, kind, subjects, allowed, _ in model.conditions:
        g = subjects[0]
        for t in range(3):
            if kind == 'TOGETHER':
                difference(3*g+t, 3*subjects[1]+t, penalty)
            elif kind == 'APART':
                add(3*g+t, 3*subjects[1]+t, penalty)
            elif t not in allowed:
                add(3*g+t, 3*g+t, penalty)
    for g, h in model.familiar:
        for t in range(3):
            if profile == 'KEEP_FAMILIAR_V01':
                difference(3*g+t, 3*h+t, 1)
            else:
                add(3*g+t, 3*h+t, 1)
    triples = [[i, j, value] for (i, j), value in sorted(terms.items()) if value]
    require(len(triples) <= 666, 'qubo_term_bound')
    for _, _, coefficient in triples:
        integer(coefficient, -1_000_000, 1_000_000)
    value = {'schema_version': 'OptimizationSpecV01', 'binding': binding_v01(problem, profile),
             'variable_mapping': mapping_v01(problem), 'capacities': [4, 4, 4],
             'condition_refs': [c[0] for c in model.conditions], 'qubo_terms': triples, 'offset': offset,
             'penalty': {'hard_minimum_if_invalid': 1, 'soft_feasible_upper': penalty-1, 'multiplier': penalty,
                         'proof': 'NONNEGATIVE_INTEGER_H_AND_BOUNDED_FEASIBLE_SOFT_V01'},
             'bounds': {'variables': 36, 'max_terms': 666, 'max_abs_coefficient': 1_000_000},
             'compiler_id': 'ORIGINAL_ONE_HOT_QUBO_V01'}
    return OptimizationSpecV01(canonical_bytes_v01(value))


def evaluate_qubo_v01(spec, bits):
    require(type(spec) is OptimizationSpecV01, 'optimization_type')
    require(type(bits) in (list, tuple) and len(bits) == 36, 'bits_shape')
    for bit in bits:
        integer(bit, 0, 1)
    value = spec.to_plain_v01()
    return value['offset'] + sum(c*bits[i]*bits[j] for i, j, c in value['qubo_terms'])


def validate_assignment_v01(problem, assignment, profile):
    model = ProblemMathV01(problem)
    bits = model.assignment_bits(assignment)
    verdicts = model.verdicts(assignment)
    h, keep, mix = model.components(bits)
    score = keep if profile == 'KEEP_FAMILIAR_V01' else mix
    model.penalty(profile)
    value = {'schema_version': 'SeatingValidationReportV01', 'binding': binding_v01(problem, profile),
             'assignment': list(assignment), 'status': 'VALID' if h == 0 else 'INVALID',
             'condition_verdicts': verdicts, 'hard_violations': [v['condition_id'] for v in verdicts if not v['satisfied']],
             'components': {'hard': h, 'keep': keep, 'mix': mix, 'objective': score},
             'ranking_key': [h != 0, score, list(assignment)], 'coverage': 'ORIGINAL_ALL_CONDITIONS',
             'validator_id': 'ORIGINAL_12_GUEST_VALIDATOR_V01'}
    return SeatingValidationReportV01(canonical_bytes_v01(value))


def candidate_set_v01(problem, profile, assignments, *, origin, provenance_ref, coverage='SUPPLIED_ONLY'):
    from .contracts_v01 import parse_candidate_set_v01
    value = {'schema_version': 'SeatingCandidateSetV01', 'binding': binding_v01(problem, profile),
             'origin': origin, 'provenance_ref': provenance_ref, 'coverage': coverage,
             'assignments': sorted([list(a) for a in assignments])}
    return parse_candidate_set_v01(canonical_bytes_v01(value), problem=problem, profile=profile,
                                  expected_origin=origin, expected_provenance_ref=provenance_ref)
