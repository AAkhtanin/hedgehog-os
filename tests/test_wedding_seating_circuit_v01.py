"""Explicit optional numpy/SDK tests; no AWS object, network or native fixture."""
from collections import Counter
from functools import lru_cache
import json
import math
import time
import unittest
from hedgehog.domains.wedding_seating import contracts_v01 as c, circuit_v02 as q
from test_wedding_seating_encoding_v01 import shared_encodings

EVIDENCE = {}


def errors(actual, expected, energies):
    import numpy as np
    overlap = np.vdot(expected, actual)
    phase = overlap/abs(overlap) if abs(overlap) else 1
    aligned = actual/phase
    return {'amplitude_max': float(np.max(np.abs(aligned-expected))),
            'probability_max': float(np.max(np.abs(np.abs(actual)**2-np.abs(expected)**2))),
            'energy_error': abs(float(np.dot(np.abs(actual)**2, energies))-float(np.dot(np.abs(expected)**2, energies))),
            'normalization_error': abs(float(np.dot(np.abs(actual), np.abs(actual)))-1)}


@lru_cache(maxsize=1)
def shared_grids():
    encodings, scale = shared_encodings()
    result = {}
    for profile, encoding in encodings.items():
        start = time.perf_counter()
        grid = q.select_grid_v02(encoding, scale)
        result[profile] = grid
        EVIDENCE.setdefault('grids', {})[profile] = {'seconds': time.perf_counter()-start, **grid}
    return result


class CircuitTests(unittest.TestCase):
    def test_grid_selection_and_exact_angle_descriptors(self):
        grids = shared_grids()
        encodings, scale = shared_encodings()
        for profile, grid in grids.items():
            self.assertEqual(len(grid['rows']), 768)
            keys = [(r['gamma_index'], r['beta_index']) for r in grid['rows']]
            self.assertEqual(keys, [(j,k) for j in range(1,33) for k in range(1,25)])
            for row in grid['rows']:
                self.assertEqual(row['loss_key'], q.loss_key_v02(row['loss']))
            selected = min(grid['rows'], key=lambda r:(r['loss_key'], r['gamma_index'], r['beta_index']))
            self.assertEqual(grid['selected'], selected)
            descriptor = q.circuit_descriptor_v02(encodings[profile], scale, selected['gamma_index'], selected['beta_index']).to_plain_v01()
            self.assertEqual(descriptor['abstract_counts'], {'h': 10, 'cnot': 310, 'rz': 105, 'rx': 10, 'measure': 10})
            self.assertEqual(descriptor['gamma_pi'], [selected['gamma_index'], 2])
            self.assertEqual(descriptor['beta_pi'], [selected['beta_index'], 24])
        self.assertEqual(q.loss_key_v02(0.5), 500000000000)

    def test_independent_gate_execution_zero_sign_and_selected(self):
        encodings, scale = shared_encodings()
        for profile, encoding in encodings.items():
            selected = shared_grids()[profile]['selected']
            angles = [(0,0), (0,.31), (.71,0), (.71,-.29), (-.71,.29), (.81,.29),
                      (math.pi*selected['gamma_index']/2, math.pi*selected['beta_index']/24)]
            records = []
            energies = encoding.to_plain_v01()['energies']
            for gamma, beta in angles:
                expected = q.direct_state_v02(encoding, scale, gamma, beta)
                operations = q.gate_operations_v02(encoding, scale, gamma, beta)
                actual = q.gate_state_v02(operations)
                metrics = errors(actual, expected, energies)
                self.assertLess(metrics['amplitude_max'], 1e-12)
                self.assertLess(metrics['probability_max'], 1e-12)
                self.assertLess(metrics['energy_error'], 1e-10)
                self.assertLess(metrics['normalization_error'], 1e-12)
                records.append({'gamma': gamma, 'beta': beta, **metrics})
            EVIDENCE.setdefault('gate_equivalence', {})[profile] = records

    def test_actual_sdk_serialized_program_and_mutants(self):
        import numpy as np
        encodings, scale = shared_encodings()
        programs, refusals = {}, []
        for profile, encoding in encodings.items():
            selected = shared_grids()[profile]['selected']
            j, k = selected['gamma_index'], selected['beta_index']
            captured = q.build_sdk_program_v02(encoding, scale, j, k)
            raw = captured['program_json']
            value = json.loads(raw)
            self.assertEqual(value['source'].encode(), captured['source'])
            operations, measurement = q.parse_openqasm_program_v02(raw)
            self.assertEqual(Counter(op[0] for op in operations), {'h':10, 'cnot':310, 'rz':105, 'rx':10})
            self.assertEqual(measurement, tuple((q,q) for q in range(10)))
            expected = q.direct_state_v02(encoding, scale, math.pi*j/2, math.pi*k/24)
            actual, _ = q.execute_openqasm_program_v02(raw)
            metrics = errors(actual, expected, encoding.to_plain_v01()['energies'])
            self.assertLess(metrics['amplitude_max'], 1e-12)
            self.assertLess(metrics['probability_max'], 1e-12)
            self.assertLess(metrics['energy_error'], 1e-10)
            lines = value['source'].splitlines()
            first_rz = next(i for i, line in enumerate(lines) if line.startswith('rz('))
            first_cnot = next(i for i, line in enumerate(lines) if line.startswith('cnot'))
            for kind in ('sign', 'wire'):
                modified = lines.copy()
                if kind == 'sign':
                    line = modified[first_rz]
                    text, suffix = line.split(')')
                    modified[first_rz] = f'rz({-float(text[3:])})'+suffix
                else:
                    modified[first_cnot] = 'cnot q[8], q[9];'
                mutant = dict(value, source='\n'.join(modified))
                changed, _ = q.execute_openqasm_program_v02(json.dumps(mutant).encode())
                difference = errors(changed, expected, encoding.to_plain_v01()['energies'])
                self.assertGreater(difference['amplitude_max'], 1e-6)
                refusals.append({'profile': profile, 'mutant': kind, 'status': 'EQUIVALENCE_REFUSED', **difference})
            for suffix in ('x q[0];', 'barrier q;', 'rx(foo) q[0];'):
                mutant = dict(value, source='\n'.join(lines[:3]+[suffix]+lines[3:]))
                with self.assertRaisesRegex(ValueError, 'unsupported_qasm_statement'):
                    q.execute_openqasm_program_v02(json.dumps(mutant).encode())
            mutant = dict(value, inputs={'gamma': 1})
            with self.assertRaisesRegex(ValueError, 'program_schema_inputs'):
                q.parse_openqasm_program_v02(json.dumps(mutant).encode())
            mutant = dict(value, source=value['source'].replace('b[0] = measure q[0];', 'b[0] = measure q[1];'))
            with self.assertRaisesRegex(ValueError, 'measurement_wiring'):
                q.parse_openqasm_program_v02(json.dumps(mutant).encode())
            positive_after, _ = q.execute_openqasm_program_v02(raw)
            self.assertLess(errors(positive_after, expected, encoding.to_plain_v01()['energies'])['amplitude_max'], 1e-12)
            programs[profile] = {'descriptor': captured['descriptor'].to_plain_v01(), 'program_json': raw.decode(),
                'source': captured['source'].decode(), 'program_sha256': captured['program_sha256'],
                'source_sha256': captured['source_sha256'], 'measurement': measurement, 'metrics': metrics,
                'pre_measurement_state': [[float(z.real), float(z.imag)] for z in actual]}
        EVIDENCE['programs'], EVIDENCE['serialized_mutants'] = programs, refusals
