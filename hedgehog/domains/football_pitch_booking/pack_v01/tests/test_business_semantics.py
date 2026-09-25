"""Reviewer-only tests of the public MOCK business-semantics declaration."""
import unittest
from hedgehog.kernel import effect_firewall_v01 as firewall
from candidate_domain.effect import admit

class BookingBusinessSemanticsTests(unittest.TestCase):
    def test_admitted_operation_namespace_and_exhaustive_typed_mapping(self):
        # Admission observes the actual module-level callbacks. No executor or
        # dispatch is called here; source review and runner permission are separate.
        admitted=admit('venue:own:semantics')
        snapshot=firewall.snapshot_admitted_capability_v01(admitted)
        self.assertEqual(firewall.validate_capability_admission_snapshot_v01(snapshot),())
        definition=snapshot.definition
        semantics=definition.business_semantics
        self.assertEqual(definition.effect_kind,'MOCK_CONSEQUENTIAL')
        self.assertEqual(definition.operation_id,'football.book.v01')
        self.assertEqual(definition.operation_id,semantics.operation_key)
        self.assertEqual(semantics.operation_key,semantics.logical_effect_namespace)
        self.assertEqual(semantics.selected_action_class,'mock_action:football_booking')
        self.assertEqual(semantics.logical_effect_class,'BOOK')
        self.assertEqual(semantics.business_object_class,'BOOKING')
        self.assertEqual(semantics.business_object_namespace,'football.registry.v01')
        self.assertEqual(definition.resource_refs,('venue:own:semantics',))
        self.assertEqual(
            tuple((b.input_name,b.source_kind,b.source_name,b.value_type) for b in semantics.input_bindings),
            (('device_ref','TARGET_RECORD','device_ref','REFERENCE'),
             ('payload_json','RECORD','payload_json','TEXT')))
        self.assertEqual(
            tuple((f.name,f.value_type,f.required,f.consequential) for f in definition.input_fields),
            (('device_ref','REFERENCE',True,True),('payload_json','TEXT',True,True)))

        declared=dict(operation_key=semantics.operation_key,
            selected_action_class=semantics.selected_action_class,
            logical_effect_class=semantics.logical_effect_class,
            logical_effect_namespace=semantics.logical_effect_namespace,
            business_object_class=semantics.business_object_class,
            business_object_namespace=semantics.business_object_namespace,
            input_bindings=semantics.input_bindings)
        # Reproduce the reported declaration mismatch at the unchanged public guard.
        with self.assertRaisesRegex(ValueError,'^capability_business_operation$'):
            firewall.build_capability_business_semantics_v01(
                **dict(declared,logical_effect_namespace='football.booking.v01'))
        # Equality alone is insufficient: the existing MOCK action prefix remains required.
        with self.assertRaisesRegex(ValueError,'^capability_business_operation$'):
            firewall.build_capability_business_semantics_v01(
                **dict(declared,selected_action_class='football_booking'))

        # A lawful declaration still works after those scoped construction refusals.
        rebuilt=firewall.build_capability_business_semantics_v01(**declared)
        self.assertEqual(rebuilt,semantics)
        continued=firewall.snapshot_admitted_capability_v01(admit('venue:own:semantics'))
        self.assertEqual(firewall.validate_capability_admission_snapshot_v01(continued),())
        self.assertEqual(continued.definition,definition)
