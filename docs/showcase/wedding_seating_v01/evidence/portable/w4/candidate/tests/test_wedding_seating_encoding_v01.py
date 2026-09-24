from functools import lru_cache
import unittest
from hedgehog.domains.wedding_seating import contracts_v01 as c, encoding_v02 as e
from test_wedding_seating_contracts_v01 import problem, changed_problem
from test_wedding_seating_math_v01 import shared_reference, independent_components

EVIDENCE = {}


@lru_cache(maxsize=1)
def shared_encodings():
    values = {profile: e.compile_encoding_v02(problem(), profile) for profile in c.PROFILES}
    scale = e.common_scale_v02(tuple(values.values()))
    EVIDENCE['encodings'] = {k: v.to_plain_v01() for k, v in values.items()}
    EVIDENCE['common_scale'] = scale
    return values, scale


class EncodingTests(unittest.TestCase):
    def test_all_states_original_qubo_polynomial_and_pauli(self):
        p, model, specs, solved, _ = shared_reference()
        encodings, scale = shared_encodings()
        self.assertEqual(scale, 4096)
        rows = {}
        for profile in c.PROFILES:
            encoding = encodings[profile]
            data, spec = encoding.to_plain_v01(), specs[profile].to_plain_v01()
            rows[profile] = []
            nonzero = [(mask, num) for mask, num in enumerate(data['pauli_numerators']) if mask and num]
            self.assertEqual(len(nonzero), 105)
            self.assertEqual(max(mask.bit_count() for mask, _ in nonzero), 4)
            self.assertEqual(e.walsh_transform_v02(data['pauli_numerators']), tuple(1024*x for x in data['energies']))
            feasible = []
            for state in range(1024):
                assignment, bits = e.decode_basis_v02(encoding, state)
                h, keep, mix = independent_components(p.to_plain_v01(), bits)
                energy = spec['penalty']['multiplier']*h + (keep if profile == c.PROFILES[0] else mix)
                self.assertEqual(energy, spec['offset']+sum(n*bits[i]*bits[j] for i, j, n in spec['qubo_terms']))
                self.assertEqual(energy, sum(n for mask, n in data['monomials'] if state & mask == mask))
                pauli_num = sum(n * (-1 if (state & mask).bit_count() & 1 else 1) for mask, n in enumerate(data['pauli_numerators']))
                self.assertEqual(pauli_num, 1024*energy)
                self.assertEqual(energy, data['energies'][state])
                if h == 0:
                    feasible.append(assignment)
                if -1 in assignment:
                    self.assertGreater(h, 0)
                rows[profile].append([state, h, keep, mix, energy])
            self.assertEqual(sorted(feasible), solved[profile]['feasible'])
            self.assertEqual(len(set(feasible)), len(feasible))
        EVIDENCE['all_2048_state_equalities'] = rows

    def test_structural_unsupported_and_foreign_encoding(self):
        p = problem()
        for remove in ('condition_01', 'condition_08'):
            changed = p.to_plain_v01()
            changed['hard_conditions'] = [x for x in changed['hard_conditions'] if x['condition_id'] != remove]
            with self.assertRaisesRegex(c.WeddingContractError, 'UNSUPPORTED_ENCODING'):
                e.compile_encoding_v02(changed_problem(changed), c.PROFILES[0])
        encoding = shared_encodings()[0][c.PROFILES[0]]
        self.assertEqual(e.parse_encoding_v02(encoding.canonical, problem=p, profile=c.PROFILES[0]), encoding)
        bad = encoding.to_plain_v01()
        bad['fixed_table'] = 1
        with self.assertRaisesRegex(c.WeddingContractError, 'encoding_source_derivation'):
            e.parse_encoding_v02(c.canonical_bytes_v01(bad), problem=p, profile=c.PROFILES[0])
        with self.assertRaisesRegex(c.WeddingContractError, 'encoding_source_derivation'):
            e.parse_encoding_v02(encoding.canonical, problem=p, profile=c.PROFILES[1])

    def test_each_basis_and_permuted_measurement_columns(self):
        encoding = shared_encodings()[0][c.PROFILES[0]]
        permutation = [9, 1, 8, 0, 7, 2, 6, 3, 5, 4]
        for state in range(1024):
            for order in (list(range(10)), permutation):
                row = [(state >> q) & 1 for q in order]
                self.assertEqual(e.measurement_index_v02(row, order), state)
        outcomes = []
        for start in (0, 512):
            raw = {'schema_version': 'WeddingRawMeasurementsV01', 'origin': 'CONTROLLED_FIXTURE', 'shots': 512,
                   'measuredQubits': permutation,
                   'measurements': [[(state >> q) & 1 for q in permutation] for state in range(start, start+512)]}
            result = e.decode_samples_v02(c.canonical_bytes_v01(raw), encoding=encoding, problem=problem(), profile=c.PROFILES[0], expected_shots=512)
            outcomes.extend(result['outcomes'])
        self.assertEqual([o['state'] for o in outcomes], list(range(1024)))
        self.assertEqual(sum(o['status'] == 'VALID' for o in outcomes), 24)
        self.assertEqual(sum(o['status'] == 'INVALID_CODE_3' for o in outcomes), 1024-3**5)
        self.assertTrue(all(o['report']['status'] == 'VALID' for o in outcomes if o['status'] == 'VALID'))
        EVIDENCE['codec'] = {'basis_mappings': 2048, 'states': len(outcomes), 'valid_original': 24,
                             'code3_refused': 1024-3**5, 'origin': 'CONTROLLED_FIXTURE',
                             'occurrences': [[o['state'], o['occurrences'], o['status']] for o in outcomes]}

    def test_wire_refusals_and_no_sample_is_not_unsat(self):
        from copy import deepcopy
        encoding = shared_encodings()[0][c.PROFILES[0]]
        positive = {'schema_version': 'WeddingRawMeasurementsV01', 'origin': 'CONTROLLED_FIXTURE', 'shots': 1,
                    'measuredQubits': list(range(10)), 'measurements': [[1]*10]}
        def consume(value):
            return e.decode_samples_v02(c.canonical_bytes_v01(value), encoding=encoding, problem=problem(), profile=c.PROFILES[0], expected_shots=1)
        result = consume(positive)
        self.assertEqual(result['status'], 'NO_VALID_PROVIDER_SAMPLE')
        self.assertEqual(result['outcomes'][0]['status'], 'INVALID_CODE_3')
        mutants = []
        for field, value in [('measuredQubits', [0]*10), ('measuredQubits', list(range(9))),
                             ('shots', 2), ('shots', True), ('shots', 1001), ('measurements', [[0]*9]),
                             ('measurements', [[True]+[0]*9]), ('origin', 'QPU_RESULT_OBSERVED')]:
            bad = deepcopy(positive)
            bad[field] = value
            mutants.append(bad)
        bad = deepcopy(positive)
        bad['measurement_counts'] = {'0000000000': 1}
        mutants.append(bad)
        reasons = []
        for bad in mutants:
            with self.assertRaises(c.WeddingContractError) as raised:
                consume(bad)
            reasons.append(str(raised.exception))
        with self.assertRaisesRegex(c.WeddingContractError, 'wire_size'):
            e.decode_samples_v02(b' '*(8*1024*1024+1), encoding=encoding, problem=problem(), profile=c.PROFILES[0], expected_shots=1)
        self.assertEqual(consume(positive), result)
        EVIDENCE['codec_negative_reasons'] = reasons
