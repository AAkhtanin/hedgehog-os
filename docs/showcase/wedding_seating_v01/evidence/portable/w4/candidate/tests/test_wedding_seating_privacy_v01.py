from copy import deepcopy
from dataclasses import replace
import unittest
from hedgehog.domains.wedding_seating import contracts_v01 as c, privacy_v01 as p
from hedgehog.domains.wedding_seating.math_v01 import compile_optimization_v01
from test_wedding_seating_contracts_v01 import problem, semantic_inputs, SOURCE_HASH, SOURCE_REFS

EVIDENCE = {}


def policy():
    source = problem().to_plain_v01()
    return p.DisclosurePolicyV01(source['disclosure_profile_ref'], True, tuple(source['guest_ids']),
        tuple(t['table_id'] for t in source['table_records']), tuple(c['condition_id'] for c in source['hard_conditions']),
        SOURCE_REFS, tuple(('intent:'+name, text) for name, text in semantic_inputs()['safe_intents'].items()))


class PrivacyTests(unittest.TestCase):
    def test_private_split_and_role_specific_serialized_projections(self):
        original = problem()
        local = {'schema_version': 'WeddingLocalPrivateV01', 'problem': original.to_plain_v01(),
                 'private_registry': [{'guest_id': guest, 'name': 'Protected Synthetic Name '+str(i),
                     'contact': 'synthetic-private@example.invalid', 'private_reason': 'LOCAL_PRIVATE_REASON',
                     'canary': 'LOCAL_ONLY_CANARY_7941'} for i, guest in enumerate(original.to_plain_v01()['guest_ids'])]}
        checked, private = p.local_intake_v01(c.canonical_bytes_v01(local), expected_source_bundle_hash=SOURCE_HASH, expected_source_refs=SOURCE_REFS)
        self.assertEqual(checked, original)
        self.assertEqual(private.to_plain_v01()['projection'], 'LOCAL_PRIVATE')
        expected = [p.semantic_projection_v01(checked, role, policy=policy()) for role in ('ORCHESTRATOR', 'REQUIREMENT_ARCHITECT')]
        spec = compile_optimization_v01(checked, 'KEEP_FAMILIAR_V01')
        expected.append(p.numeric_projection_v01(spec, problem=checked, profile='KEEP_FAMILIAR_V01', policy=policy()))
        self.assertNotIn('guest_ids', expected[0].to_plain_v01())
        self.assertIn('hard_conditions', expected[1].to_plain_v01())
        wires = [p.serialize_approved_projection_v01(v.to_plain_v01(), independently_expected=v) for v in expected]
        for wire in wires:
            for marker in (b'Protected Synthetic Name', b'example.invalid', b'LOCAL_PRIVATE_REASON', b'LOCAL_ONLY_CANARY_7941'):
                self.assertNotIn(marker, wire)
        for marker in (b'guest_', b'table_', b'owner_root', b'source_ref', b'reason'):
            self.assertNotIn(marker, wires[2])
        EVIDENCE['serialized_projections'] = {'classification': 'SERIALIZED_PROJECTION_CHECKED_NOT_EGRESS',
                                            'values': [v.to_plain_v01() for v in expected]}

    def test_actual_wire_mutants_and_unknown_private_paths_refuse(self):
        expected = p.semantic_projection_v01(problem(), 'REQUIREMENT_ARCHITECT', policy=policy())
        fields = ('private_registry', 'contact', 'private_reason', 'reason', 'job_label', 'attachment', 'redirect', 'endpoint')
        rejected = []
        for field in fields:
            wire = expected.to_plain_v01()
            wire[field] = 'LOCAL_ONLY_CANARY_7941'
            with self.assertRaisesRegex(c.WeddingContractError, 'serialized_projection_mismatch'):
                p.serialize_approved_projection_v01(wire, independently_expected=expected)
            rejected.append(field)
        wire = expected.to_plain_v01()
        wire['hard_conditions'][0]['private_reason'] = 'Protected Synthetic Name'
        with self.assertRaisesRegex(c.WeddingContractError, 'serialized_projection_mismatch'):
            p.serialize_approved_projection_v01(wire, independently_expected=expected)
        wire = expected.to_plain_v01()
        wire['safe_intent'] += ' synthetic-private@example.invalid'
        with self.assertRaisesRegex(c.WeddingContractError, 'serialized_projection_mismatch'):
            p.serialize_approved_projection_v01(wire, independently_expected=expected)
        self.assertEqual(p.serialize_approved_projection_v01(expected.to_plain_v01(), independently_expected=expected), expected.canonical)
        EVIDENCE['privacy_mutations'] = {'rejected_fields': rejected, 'nested_reason_and_free_text': 'REFUSED', 'positive_after': 'PASS'}

    def test_explicit_disclosure_denial_and_finite_intent_dictionary(self):
        denied = replace(policy(), structural_disclosure=False)
        with self.assertRaisesRegex(c.WeddingContractError, 'STRUCTURAL_DISCLOSURE_DENIED'):
            p.semantic_projection_v01(problem(), 'ORCHESTRATOR', policy=denied)
        spec = compile_optimization_v01(problem(), 'KEEP_FAMILIAR_V01')
        self.assertEqual(spec.to_plain_v01()['bounds']['variables'], 36)
        with self.assertRaisesRegex(c.WeddingContractError, 'STRUCTURAL_DISCLOSURE_DENIED'):
            p.numeric_projection_v01(spec, problem=problem(), profile='KEEP_FAMILIAR_V01', policy=denied)
        safe = semantic_inputs()['safe_intents']['A']
        self.assertEqual(p.resolve_local_intent_v01(safe, approved_exact_texts={safe: 'intent:A'}), 'intent:A')
        for private_text in ('Seat Protected Synthetic Name with friends', 'Email me at synthetic-private@example.invalid', safe+' LOCAL_ONLY_CANARY_7941'):
            with self.assertRaisesRegex(c.WeddingContractError, 'NEEDS_LOCAL_REDACTION'):
                p.resolve_local_intent_v01(private_text, approved_exact_texts={safe: 'intent:A'})
        self.assertEqual(p.semantic_projection_v01(problem(), 'ORCHESTRATOR', policy=policy()).to_plain_v01()['safe_intent'], safe)
