"""Reviewer-only regression for exact public Root/descent bindings; never run by author."""
import tempfile
import unittest
from pathlib import Path
from hedgehog.drs import LocalDRS
from hedgehog import drs_semantic_address_v01 as address, drs_memory_resolution_v01 as memory
from hedgehog.kernel import integrity_replay_v01 as integrity, root_decision_v01 as roots
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n, gate5_exchange_v01 as x
from candidate_domain.memory import descent
from candidate_domain.native import review
from candidate_domain.profile import SUMMARY
from candidate_domain.publication import envelope
from candidate_domain.storage import read

class NativeDescentBindingTests(unittest.TestCase):
    def test_exact_plan_predicate_owner_and_lawful_continuation(self):
        local_root='root:own:descent_reader'
        now=x.clock()
        # Local component fixture only: this does not assert peer signature verification.
        # Production checks the full signed pointer before calling this metadata adapter.
        pointer=dict(publisher_root_id='root:own:metadata_source',
            source_record_ref='source:own:metadata',pointer_id='pointer:own:metadata',
            body_sha256=c.sha(dict(kind='own_metadata_fixture')),safe_summary=SUMMARY,
            time_envelope=envelope(now,300))
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            decision_id=descent(pointer,local_root,folder,now,now+300)
            proof=read(folder/'pointer_descent.json')
            saved_review=read(folder/'descent_review.json')
            plan=n.rebuilt(memory.build_retrieval_plan_v01,proof['plan'])
            budget=n.rebuilt(memory.build_memory_descent_budget_v01,proof['request']['approved_budget'])
            claim=saved_review['inputs']['root_review_packet']['synthesis_proposal']['normalized_claims'][0]
            self.assertEqual(claim['predicate'],'approve_controlled_memory_descent_plan_v01')
            self.assertEqual(claim['claim_id'],plan.retrieval_plan_id)
            self.assertEqual(claim['subject'],plan.semantic_address_id)
            self.assertEqual(claim['object_or_value'],proof['plan'])
            self.assertEqual(claim['authority_class'],'NONE')
            self.assertEqual(saved_review['result']['decision_id'],decision_id)
            self.assertEqual(proof['request']['root_decision_id'],decision_id)
            self.assertTrue(proof['result']['limits_respected'])
            self.assertFalse(proof['result']['creates_permission'])
            self.assertFalse(proof['result']['creates_authority'])
            self.assertEqual(proof['result']['safe_summaries'],[SUMMARY])

            # Reconstruct stored metadata, never a Root grant. Every check below receives
            # a fresh live local Root kernel/input/result from the public review adapter.
            record_id=proof['request']['approved_record_ids'][0]
            stored=LocalDRS(folder/'drs').read_record('work',record_id)['content']['record']
            record=n.rebuilt(address.build_meaning_record_v01,dict(stored,
                semantic_address=n.rebuilt(address.build_semantic_address_v01,stored['semantic_address']),
                time_envelope=n.rebuilt(address.build_drs_time_envelope_v01,stored['time_envelope']),
                authority_envelope=n.rebuilt(address.build_drs_authority_envelope_v01,stored['authority_envelope'])))
            checks=dict(plan_matches_saved_query=plan.query_id==proof['request']['query_id'],
                        exact_record=record.meaning_record_id==record_id)

            def request_for(live):
                fingerprint=integrity.domain_separated_sha256_hex_v01(
                    domain='hedgehog:drs:memory_descent_root_result_binding:v01',
                    payload=c.canonical(roots.root_decision_result_to_plain_dict_v01(live[2])))
                return memory.build_memory_descent_request_v01(
                    retrieval_plan_id=plan.retrieval_plan_id,query_id=plan.query_id,
                    owning_local_root_id=local_root,root_kernel_id=live[0].kernel_id,
                    root_decision_input_id=live[1].decision_input_id,root_decision_id=live[2].decision_id,
                    root_decision_hash=fingerprint,requested_descent_class='SUMMARY_ONLY',
                    approved_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,
                    approved_budget=budget,approved_record_ids=(record_id,),
                    approved_memory_pointer_ids=(),approved_artifact_pointer_ids=())

            def execute(live):
                return memory.execute_local_memory_descent_v01(
                    retrieval_plan=plan,proposed_budget=budget,descent_request=request_for(live),
                    root_kernel=live[0],root_decision_input=live[1],root_decision_result=live[2],
                    source_records=(record,))

            generic=review(local_root,plan.query_id,plan.retrieval_plan_id,plan.semantic_address_id,
                checks,proof['plan'],x.clock(),folder,'generic_review',window=(now,now+300))
            self.assertEqual(generic[2].decision,'ACCEPT')
            with self.assertRaisesRegex(ValueError,'^drs_root_decision_binding_invalid$'):
                execute(generic)

            foreign=review('root:own:another_reader',plan.query_id,plan.retrieval_plan_id,plan.semantic_address_id,
                checks,proof['plan'],x.clock(),folder,'foreign_review',window=(now,now+300),
                predicate='approve_controlled_memory_descent_plan_v01')
            self.assertEqual(foreign[2].decision,'ACCEPT')
            with self.assertRaisesRegex(ValueError,'^drs_root_owner_mismatch$'):
                execute(foreign)

            current=review(local_root,plan.query_id,plan.retrieval_plan_id,plan.semantic_address_id,
                checks,proof['plan'],x.clock(),folder,'current_review',window=(now,now+300),
                predicate='approve_controlled_memory_descent_plan_v01')
            result=execute(current)
            self.assertTrue(result.limits_respected)
            self.assertEqual(result.safe_summaries,(SUMMARY,))
            self.assertFalse(result.creates_authority)
            self.assertFalse(result.creates_permission)
