"""Focused stdlib tests. No core collectors, native fixtures or providers."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import unittest
from hedgehog.domains.wedding_seating import contracts_v01 as c

ROOT = Path(__file__).resolve().parents[1]
SOURCE_HASH = 'f9b46b070624407e150424008fb3e933773751f54d7b5dacff834ae6855e9fa4'
SOURCE_REFS = ('source:w1:hard',)
EVIDENCE = {}


def problem():
    return c.parse_problem_v01((ROOT/'fixtures/wedding_seating/reference_problem_v01.json').read_bytes(),
                              expected_source_bundle_hash=SOURCE_HASH, expected_source_refs=SOURCE_REFS)


def changed_problem(value):
    return c.parse_problem_v01(c.canonical_bytes_v01(value), expected_source_bundle_hash=SOURCE_HASH, expected_source_refs=SOURCE_REFS)


def semantic_inputs():
    return json.loads((ROOT/'fixtures/wedding_seating/semantic_proposals_v01.json').read_text())


def parse_proposal(value, expected=None):
    anchor = expected or value
    return c.parse_semantic_proposal_v01(c.canonical_bytes_v01(value), problem=problem(),
        expected_role=anchor['role'], expected_request_ref=anchor['request_ref'],
        expected_actor_ref=anchor['actor_ref'], expected_model_ref=anchor['model_ref'],
        expected_capture_ref=anchor['capture_ref'], expected_source_refs=SOURCE_REFS)


class ContractsTests(unittest.TestCase):
    def test_coherent_foreign_profile_and_mapping_are_not_current(self):
        from hedgehog.domains.wedding_seating.math_v01 import compile_optimization_v01
        p = problem()
        keep = compile_optimization_v01(p, c.PROFILES[0])
        foreign_profile = compile_optimization_v01(p, c.PROFILES[1])
        with self.assertRaisesRegex(c.WeddingContractError, 'current_problem_profile_mapping_binding'):
            c.parse_optimization_spec_v01(foreign_profile.canonical, problem=p, profile=c.PROFILES[0])
        altered = keep.to_plain_v01()
        # Coherent local renumbering, including its own recalculated identity.
        altered['variable_mapping'] = list(reversed(altered['variable_mapping']))
        for i, item in enumerate(altered['variable_mapping']):
            item['index'] = i
        altered['qubo_terms'] = sorted([[min(35-i, 35-j), max(35-i, 35-j), n] for i,j,n in altered['qubo_terms']])
        altered['binding']['mapping_ref'] = c.identity_v01(altered['variable_mapping'])
        with self.assertRaisesRegex(c.WeddingContractError, 'current_problem_profile_mapping_binding'):
            c.parse_optimization_spec_v01(c.canonical_bytes_v01(altered), problem=p, profile=c.PROFILES[0])
        bad = keep.to_plain_v01()
        bad['binding']['problem_revision'] = True
        with self.assertRaisesRegex(c.WeddingContractError, 'current_problem_profile_mapping_binding'):
            c.parse_optimization_spec_v01(c.canonical_bytes_v01(bad), problem=p, profile=c.PROFILES[0])
        self.assertEqual(c.parse_optimization_spec_v01(keep.canonical, problem=p, profile=c.PROFILES[0]), keep)
        EVIDENCE['coherent_foreign_controls'] = {'foreign_profile': 'REFUSED', 'renumbered_mapping_with_new_hash': 'REFUSED',
                                               'bool_revision': 'REFUSED', 'unchanged_positive': 'PASS'}

    def test_numeric_wire_mutations_and_explicit_bounds(self):
        from hedgehog.domains.wedding_seating import math_v01 as m, privacy_v01 as privacy
        from test_wedding_seating_privacy_v01 import policy
        p, profile = problem(), c.PROFILES[0]
        spec = m.compile_optimization_v01(p, profile)
        expected = privacy.numeric_projection_v01(spec, problem=p, profile=profile, policy=policy())
        for field in ('reason', 'job_label', 'attachment', 'redirect', 'private_registry'):
            bad = expected.to_plain_v01()
            bad[field] = 'LOCAL_ONLY_CANARY_7941'
            with self.assertRaisesRegex(c.WeddingContractError, 'serialized_projection_mismatch'):
                privacy.serialize_approved_projection_v01(bad, independently_expected=expected)
        for value in ('x'*97, '', 'name with spaces'):
            bad = p.to_plain_v01()
            bad['owner_root_id'] = value
            with self.assertRaisesRegex(c.WeddingContractError, 'opaque_id'):
                changed_problem(bad)
        with self.assertRaisesRegex(c.WeddingContractError, 'collection_bound'):
            c.parse_problem_v01(p.canonical, expected_source_bundle_hash=SOURCE_HASH,
                                expected_source_refs=tuple(f'source:{i}' for i in range(65)))
        bad = spec.to_plain_v01()
        bad['qubo_terms'].append([0,0,1])
        with self.assertRaisesRegex(c.WeddingContractError, 'optimization_exact_derivation'):
            c.parse_optimization_spec_v01(c.canonical_bytes_v01(bad), problem=p, profile=profile)
        report = m.validate_assignment_v01(p, [0]*4+[1]*4+[2]*4, profile)
        bad = report.to_plain_v01()
        bad['components']['hard'] = False
        with self.assertRaisesRegex(c.WeddingContractError, 'validation_report_derivation'):
            c.parse_validation_report_v01(c.canonical_bytes_v01(bad), problem=p, profile=profile, assignment=[0]*4+[1]*4+[2]*4)
        self.assertEqual(privacy.serialize_approved_projection_v01(expected.to_plain_v01(), independently_expected=expected), expected.canonical)

    def test_canonical_closed_problem_and_isolation(self):
        p = problem()
        plain = p.to_plain_v01()
        plain['guest_ids'].reverse()
        plain['hard_conditions'].reverse()
        plain['table_records'].reverse()
        plain['familiarity_pairs'].reverse()
        self.assertEqual(changed_problem(plain), p)
        plain['hard_conditions'][0]['hard'] = False
        self.assertTrue(all(v['hard'] for v in p.to_plain_v01()['hard_conditions']))
        with self.assertRaises(FrozenInstanceError):
            p.canonical = b'{}'
        EVIDENCE['canonical_problem'] = p.to_plain_v01()

    def test_wire_limits_and_exact_types(self):
        cases = [(b'{"x":1,"x":2}', 'duplicate_key'), (b'{"x":0.0}', 'normative_float'),
                 (b'{"x":NaN}', 'normative_float'), (b'{"x":Infinity}', 'normative_float'),
                 (b'['*17+b'0'+b']'*17, 'depth_bound'), (b' '* (c.MAX_BYTES+1), 'wire_size'),
                 (b'2147483648', 'integer_bound'), (b'"\\ud800"', 'text_bound')]
        for wire, reason in cases:
            with self.subTest(reason=reason), self.assertRaisesRegex(c.WeddingContractError, reason):
                c.parse_json_v01(wire)
        p = problem().to_plain_v01()
        for key, value, reason in [('problem_revision', True, 'integer_bound'),
                                   ('owner_root_id', '../private', 'opaque_id'),
                                   ('guest_ids', p['guest_ids']+[p['guest_ids'][0]], 'collection_bound'),
                                   ('source_bundle_hash', '0'*64, 'source_bundle_binding')]:
            bad = deepcopy(p)
            bad[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(c.WeddingContractError, reason):
                changed_problem(bad)
        for key in ('endpoint', 'shell', 'permission', 'token', 'code'):
            bad = deepcopy(p)
            bad[key] = 'forbidden'
            with self.assertRaisesRegex(c.WeddingContractError, 'closed_keys'):
                changed_problem(bad)
        self.assertEqual(problem().to_plain_v01(), p)

    def test_conditions_and_sources_are_not_model_policy(self):
        p = problem().to_plain_v01()
        for key, val, reason in [('hard', False, 'hard_policy'), ('subjects', ['absent', 'guest_02'], 'unknown_guest'),
                                 ('source_ref', 'source:foreign', 'condition_source_binding')]:
            bad = deepcopy(p)
            bad['hard_conditions'][0][key] = val
            with self.subTest(key=key), self.assertRaisesRegex(c.WeddingContractError, reason):
                changed_problem(bad)
        bad = deepcopy(p)
        bad['hard_conditions'] = [dict(p['hard_conditions'][0], condition_id=f'condition:{i}') for i in range(65)]
        with self.assertRaisesRegex(c.WeddingContractError, 'collection_bound'):
            changed_problem(bad)
        self.assertEqual(len(problem().to_plain_v01()['hard_conditions']), 8)

    def test_distinct_controlled_semantic_shapes(self):
        inputs = semantic_inputs()['proposals']
        outputs = [parse_proposal(v).to_plain_v01() for v in inputs]
        self.assertEqual(outputs[1]['objective_profile'], 'KEEP_FAMILIAR_V01')
        self.assertEqual(outputs[3]['objective_profile'], 'MIX_CIRCLES_V01')
        self.assertEqual(outputs[-1]['needed_capabilities'], ['VALIDATE_ORIGINAL'])
        for field, value, reason in [('condition_refs', ['condition_01'], 'mandatory_condition_refs'),
                                    ('source_refs', ['invented:source'], 'semantic_source_binding'),
                                    ('needed_capabilities', ['EXECUTE_SHELL'], 'capability_catalogue'),
                                    ('objective_profile', 'FREE_PERMISSION', 'objective_profile'),
                                    ('problem_revision', 2, 'semantic_problem_binding'),
                                    ('capture_ref', 'capture:other', 'semantic_input_binding')]:
            bad = deepcopy(inputs[1])
            bad[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(c.WeddingContractError, reason):
                parse_proposal(bad, inputs[1])
        for field in ('endpoint', 'token', 'shell', 'code', 'permission', 'delete_conditions'):
            bad = dict(inputs[1], **{field: 'not_allowed'})
            with self.assertRaisesRegex(c.WeddingContractError, 'closed_keys'):
                parse_proposal(bad, inputs[1])
        bad = dict(inputs[0], needs=['UNKNOWN'])
        with self.assertRaisesRegex(c.WeddingContractError, 'need_catalogue'):
            parse_proposal(bad, inputs[0])
        bad = dict(inputs[0], role='ROOT')
        with self.assertRaisesRegex(c.WeddingContractError, 'semantic_role'):
            parse_proposal(bad)
        revise = dict(inputs[1], task_kind='REVISE')
        self.assertEqual(parse_proposal(revise).to_plain_v01()['task_kind'], 'REVISE')
        clarify = dict(inputs[1], task_kind='CLARIFY', objective_profile=None, unresolved=['conflict:pair'])
        self.assertEqual(parse_proposal(clarify).to_plain_v01()['unresolved'], ['conflict:pair'])
        self.assertEqual(parse_proposal(inputs[1]).to_plain_v01(), outputs[1])
        EVIDENCE['semantic_controlled'] = outputs

    def test_semantic_response_bound(self):
        v = semantic_inputs()['proposals'][0]
        args = dict(problem=problem(), expected_role=v['role'], expected_request_ref=v['request_ref'],
                    expected_actor_ref=v['actor_ref'], expected_model_ref=v['model_ref'],
                    expected_capture_ref=v['capture_ref'], expected_source_refs=SOURCE_REFS)
        with self.assertRaisesRegex(c.WeddingContractError, 'wire_size'):
            c.parse_semantic_proposal_v01(b' '*(c.SEMANTIC_BYTES+1), **args)
        for item in (dict(v, reason='x'*1025), dict(v, needs=['EXACT_SEARCH']*65)):
            with self.assertRaises(c.WeddingContractError):
                parse_proposal(item, v)
        self.assertEqual(parse_proposal(v).to_plain_v01()['task_kind'], 'GENERATE')

    def test_specs_candidates_and_reports_bind_independent_problem(self):
        from hedgehog.domains.wedding_seating.math_v01 import compile_optimization_v01, candidate_set_v01, validate_assignment_v01
        p, profile = problem(), 'KEEP_FAMILIAR_V01'
        spec = compile_optimization_v01(p, profile)
        self.assertEqual(c.parse_optimization_spec_v01(spec.canonical, problem=p, profile=profile), spec)
        for field, val in [('problem_revision', 2), ('objective_profile', 'MIX_CIRCLES_V01'), ('mapping_ref', '0'*64)]:
            bad = spec.to_plain_v01()
            bad['binding'][field] = val
            with self.assertRaisesRegex(c.WeddingContractError, 'current_problem_profile_mapping_binding'):
                c.parse_optimization_spec_v01(c.canonical_bytes_v01(bad), problem=p, profile=profile)
        assignment = [0]*4+[1]*4+[2]*4
        candidates = candidate_set_v01(p, profile, [assignment], origin='CONTROLLED_FIXTURE', provenance_ref='capture:local')
        self.assertEqual(c.parse_candidate_set_v01(candidates.canonical, problem=p, profile=profile, expected_origin='CONTROLLED_FIXTURE', expected_provenance_ref='capture:local'), candidates)
        report = validate_assignment_v01(p, assignment, profile)
        self.assertEqual(c.parse_validation_report_v01(report.canonical, problem=p, profile=profile, assignment=assignment), report)
        bad = report.to_plain_v01()
        bad['condition_verdicts'][0]['satisfied'] = False
        with self.assertRaisesRegex(c.WeddingContractError, 'validation_report_derivation'):
            c.parse_validation_report_v01(c.canonical_bytes_v01(bad), problem=p, profile=profile, assignment=assignment)
        other = p.to_plain_v01()
        other.update(problem_revision=2, parent_problem_ref=p.content_id)
        other = changed_problem(other)
        foreign = compile_optimization_v01(other, profile)
        with self.assertRaisesRegex(c.WeddingContractError, 'current_problem_profile_mapping_binding'):
            c.parse_optimization_spec_v01(foreign.canonical, problem=p, profile=profile)
        with self.assertRaisesRegex(c.WeddingContractError, 'candidate_origin'):
            candidate_set_v01(p, profile, [assignment], origin='QPU_RESULT_OBSERVED', provenance_ref='capture:local')
        EVIDENCE['typed_spec'] = spec.to_plain_v01()
        EVIDENCE['candidate_set'] = candidates.to_plain_v01()
        EVIDENCE['validation_report'] = report.to_plain_v01()
