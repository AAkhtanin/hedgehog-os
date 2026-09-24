"""Independent pair oracle and original equations, not a reference-script import."""
from copy import deepcopy
from functools import lru_cache
from itertools import combinations
import random
import time
import unittest
from hedgehog.domains.wedding_seating import contracts_v01 as c, math_v01 as m
from test_wedding_seating_contracts_v01 import problem, changed_problem

EVIDENCE = {}


def independent_components(p, bits):
    guests = p['guest_ids']
    tables = [t['table_id'] for t in p['table_records']]
    matrix = {g: {t: bits[3*i+j] for j, t in enumerate(tables)} for i, g in enumerate(guests)}
    hard = sum((sum(matrix[g].values())-1)**2 for g in guests)
    hard += sum((sum(matrix[g][t] for g in guests)-4)**2 for t in tables)
    for condition in p['hard_conditions']:
        a = condition['subjects'][0]
        if condition['predicate'] == 'ALLOWED_TABLES':
            hard += sum(matrix[a][t] for t in tables if t not in condition['tables'])
        else:
            b = condition['subjects'][1]
            for t in tables:
                if condition['predicate'] == 'APART':
                    hard += matrix[a][t]*matrix[b][t]
                else:
                    hard += matrix[a][t]+matrix[b][t]-2*matrix[a][t]*matrix[b][t]
    keep = sum(matrix[a][t]+matrix[b][t]-2*matrix[a][t]*matrix[b][t] for a, b in p['familiarity_pairs'] for t in tables)
    mix = sum(matrix[a][t]*matrix[b][t] for a, b in p['familiarity_pairs'] for t in tables)
    return hard, keep, mix


def pair_oracle(p):
    """90 assignments of six indivisible pairs, independent predicates/scoring."""
    guests, tables = p['guest_ids'], [t['table_id'] for t in p['table_records']]
    pairs = [condition['subjects'] for condition in p['hard_conditions'] if condition['predicate'] == 'TOGETHER']
    if len(pairs) != 6 or sorted(g for pair in pairs for g in pair) != sorted(guests):
        raise ValueError('oracle_requires_disjoint_pairs')
    feasible, examined = [], 0
    for left in combinations(range(6), 2):
        for middle in combinations([i for i in range(6) if i not in left], 2):
            examined += 1
            seating = {g: tables[0 if i in left else 1 if i in middle else 2] for i, pair in enumerate(pairs) for g in pair}
            valid = True
            for condition in p['hard_conditions']:
                subjects, kind = condition['subjects'], condition['predicate']
                if kind == 'TOGETHER':
                    valid &= seating[subjects[0]] == seating[subjects[1]]
                elif kind == 'APART':
                    valid &= seating[subjects[0]] != seating[subjects[1]]
                else:
                    valid &= seating[subjects[0]] in condition['tables']
            if valid:
                feasible.append(tuple(tables.index(seating[g]) for g in guests))
    feasible.sort()
    scores = {}
    for profile in c.PROFILES:
        row = {a: sum((2 if a[guests.index(g)] != a[guests.index(h)] else 0) if profile == c.PROFILES[0]
                      else int(a[guests.index(g)] == a[guests.index(h)]) for g, h in p['familiarity_pairs']) for a in feasible}
        best = min(row.values()) if row else None
        scores[profile] = {'optimum': best, 'tied_optima': [a for a in feasible if row[a] == best]}
    return {'examined': examined, 'feasible': feasible, 'profiles': scores}


@lru_cache(maxsize=1)
def shared_reference():
    started = time.perf_counter()
    p = problem()
    model = m.ProblemMathV01(p)
    specs = {profile: m.compile_optimization_v01(p, profile) for profile in c.PROFILES}
    solved = model.solve_profiles()
    oracle = pair_oracle(p.to_plain_v01())
    EVIDENCE['reference'] = {'solutions': solved, 'independent_oracle': oracle, 'seconds': time.perf_counter()-started,
                             'specs': {k: v.to_plain_v01() for k, v in specs.items()}}
    return p, model, specs, solved, oracle


class MathTests(unittest.TestCase):
    def test_full_balanced_partitions_and_independent_pair_oracle(self):
        p, model, specs, solved, oracle = shared_reference()
        self.assertEqual(oracle['examined'], 90)
        self.assertEqual(len(oracle['feasible']), 24)
        for profile, ties in zip(c.PROFILES, (2, 12)):
            self.assertEqual(solved[profile]['evaluated'], 34650)
            self.assertEqual(solved[profile]['feasible'], oracle['feasible'])
            self.assertEqual(solved[profile]['optimum'], 0)
            self.assertEqual(solved[profile]['tied_optima'], oracle['profiles'][profile]['tied_optima'])
            self.assertEqual(len(solved[profile]['tied_optima']), ties)
            self.assertEqual(solved[profile]['selected'], min(solved[profile]['tied_optima']))
        self.assertFalse(set(solved[c.PROFILES[0]]['tied_optima']) & set(solved[c.PROFILES[1]]['tied_optima']))

    def test_every_balanced_assignment_and_seeded_invalid_energy(self):
        p, model, specs, solved, _ = shared_reference()
        original = p.to_plain_v01()
        plain_specs = {k: v.to_plain_v01() for k, v in specs.items()}
        counts = {'balanced': 0, 'binary': 0, 'profile_equalities': 0}
        def compare(bits, balanced=False):
            h, keep, mix = independent_components(original, bits)
            self.assertEqual(model.components(bits), (h, keep, mix))
            for profile, soft in zip(c.PROFILES, (keep, mix)):
                s = plain_specs[profile]
                qubo = s['offset'] + sum(value*bits[i]*bits[j] for i, j, value in s['qubo_terms'])
                self.assertEqual(qubo, s['penalty']['multiplier']*h+soft)
                if h:
                    self.assertGreaterEqual(qubo, s['penalty']['multiplier'])
                counts['profile_equalities'] += 1
            counts['balanced' if balanced else 'binary'] += 1
            return h
        for assignment in model.balanced_assignments():
            bits = model.assignment_bits(assignment)
            h = compare(bits, True)
            self.assertEqual(h == 0, all(v['satisfied'] for v in model.verdicts(assignment)))
        rng = random.Random(20260923)
        invalids = [(0,)*36, (1,)*36]
        positive = list(model.assignment_bits(solved[c.PROFILES[0]]['selected']))
        for index in (0, 1, 12, 30, 32):
            value = positive.copy()
            value[index] ^= 1
            invalids.append(tuple(value))
        invalids.extend(tuple(rng.randrange(2) for _ in range(36)) for _ in range(512))
        for bits in invalids:
            compare(bits)
        self.assertEqual(counts['balanced'], 34650)
        EVIDENCE['exhaustive_equalities'] = counts

    def test_original_assignment_negative_neighbors(self):
        p = problem()
        positive = [0]*4+[1]*4+[2]*4
        self.assertEqual(m.validate_assignment_v01(p, positive, c.PROFILES[0]).to_plain_v01()['status'], 'VALID')
        for bad in (positive[:-1], positive+[0], [True]+positive[1:], [0.0]+positive[1:], [-1]+positive[1:], [3]+positive[1:]):
            with self.assertRaises(c.WeddingContractError):
                m.validate_assignment_v01(p, bad, c.PROFILES[0])
        cases = {'capacity': [0]*12, 'together': [1,0,0,0,0,1,1,1,2,2,2,2],
                 'apart': [0,0,1,1,0,0,1,1,2,2,2,2],
                 'fixed': [0,0,2,2,1,1,1,1,2,2,0,0]}
        reports = {}
        for name, bad in cases.items():
            report = m.validate_assignment_v01(p, bad, c.PROFILES[0]).to_plain_v01()
            self.assertEqual(report['status'], 'INVALID')
            self.assertTrue(report['hard_violations'])
            reports[name] = report
        self.assertEqual(m.validate_assignment_v01(p, positive, c.PROFILES[0]).to_plain_v01()['status'], 'VALID')
        EVIDENCE['original_refusals'] = reports

    def test_contradiction_preserves_both_sources(self):
        base = problem()
        changed = base.to_plain_v01()
        changed['hard_conditions'].append({'condition_id': 'conflict:pair', 'predicate': 'APART',
            'subjects': ['guest_01', 'guest_02'], 'source_ref': 'source:w1:hard', 'hard': True})
        p = changed_problem(changed)
        result = m.ProblemMathV01(p).solve(c.PROFILES[0])
        self.assertEqual(result['status'], 'UNSAT_SUPPORTED')
        self.assertEqual({x['condition_id'] for x in result['witness']}, {'condition_01', 'conflict:pair'})
        self.assertEqual(len(base.to_plain_v01()['hard_conditions']), 8)
        EVIDENCE['contradiction'] = result

    def test_omitted_compiler_constraints_cannot_override_original(self):
        original = problem()
        for cid, assignment in [('condition_07', [0,0,1,1,0,0,1,1,2,2,2,2]),
                                ('condition_08', [0,0,2,2,1,1,1,1,2,2,0,0])]:
            weak = original.to_plain_v01()
            weak['hard_conditions'] = [x for x in weak['hard_conditions'] if x['condition_id'] != cid]
            weak = changed_problem(weak)
            spec = m.compile_optimization_v01(weak, c.PROFILES[0])
            self.assertEqual(m.validate_assignment_v01(weak, assignment, c.PROFILES[0]).to_plain_v01()['status'], 'VALID')
            self.assertIn(cid, m.validate_assignment_v01(original, assignment, c.PROFILES[0]).to_plain_v01()['hard_violations'])
            supplied = spec.to_plain_v01()
            supplied['binding'] = c.binding_v01(original, c.PROFILES[0])
            with self.assertRaisesRegex(c.WeddingContractError, 'optimization_exact_derivation'):
                c.parse_optimization_spec_v01(c.canonical_bytes_v01(supplied), problem=original, profile=c.PROFILES[0])

    def test_id_rename_is_not_fixture_dispatch(self):
        original = problem()
        renamed = original.to_plain_v01()
        rename = {g: 'person_'+g[6:] for g in renamed['guest_ids']}
        renamed['guest_ids'] = [rename[g] for g in reversed(renamed['guest_ids'])]
        for condition in renamed['hard_conditions']:
            condition['subjects'] = [rename[g] for g in condition['subjects']]
        renamed['familiarity_pairs'] = [[rename[g] for g in pair] for pair in renamed['familiarity_pairs']]
        renamed = changed_problem(renamed)
        oracle = pair_oracle(renamed.to_plain_v01())
        self.assertEqual(oracle['feasible'], shared_reference()[4]['feasible'])
        model = m.ProblemMathV01(renamed)
        for profile in c.PROFILES:
            left, right = m.compile_optimization_v01(original, profile).to_plain_v01(), m.compile_optimization_v01(renamed, profile).to_plain_v01()
            self.assertEqual(left['qubo_terms'], right['qubo_terms'])
            self.assertEqual(left['offset'], right['offset'])
            self.assertNotEqual(left['binding']['problem_ref'], right['binding']['problem_ref'])
            self.assertTrue(all(all(v['satisfied'] for v in model.verdicts(a)) for a in oracle['feasible']))
