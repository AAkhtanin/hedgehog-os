"""Controlled boundary records, not provider execution or restored authority."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from hedgehog.domains.wedding_seating import native_contracts_v01 as c, qpu_contracts_v01 as q
from hedgehog.domains.wedding_seating import qpu_application_v01 as app, qpu_bridge_v01 as bridge
from hedgehog.domains.wedding_seating import encoding_v02 as enc, circuit_v02 as circuit, qpu_output_v01 as output

WORK=Path(os.environ['W4_WORK'])

class QpuControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope=json.loads((WORK/'operator_scope.json').read_text())
        cls.intake=json.loads((WORK/'basis_w3/story/A_intake.json').read_text())
        cls.records=json.loads((WORK/'basis_w3/story/A_captures.json').read_text())
        cls.grid=(WORK/'basis_w1/captures/KEEP_FAMILIAR_V01/grid.json').read_bytes()
        cls.original=(WORK/'candidate/fixtures/wedding_seating/reference_problem_v01.json').read_bytes()
        cls.owner,cls.m=app.preparation_material_v01(cls.intake,cls.records,cls.grid,request_ref='request:w4:test',original_bytes=cls.original)
        cls.numeric=q.numeric_v01(cls.m);cls.encoding=q.check_numeric_v01(cls.m,cls.numeric)
        cls.program=circuit.build_sdk_program_v02(cls.encoding,4096,9,22)['program_json']
        cls.request=bridge.request_v01(cls.scope,cls.program,'CONTROLLED-TEST-TOKEN')
        # Explicitly controlled rows. This is codec coverage, not hardware evidence.
        cls.state=next(i for i,e in enumerate(cls.encoding.to_plain_v01()['energies']) if e==0)
        cls.arn='arn:aws:braket:us-west-1:'+bridge.ACCOUNT+':quantum-task/CONTROLLED'
        cls.raw=dict(braketSchemaHeader=dict(name='braket.task_result.gate_model_task_result',version='1'),
            taskMetadata=dict(id=cls.arn,shots=1000),measuredQubits=list(range(10)),
            measurements=[[(cls.state>>q)&1 for q in range(10)] for _ in range(1000)])

    def test_captured_meaning_and_exact_numeric(self):
        self.assertEqual(self.owner.profile,'KEEP_FAMILIAR_V01')
        self.assertEqual(self.m['semantics'][1]['capture_ref'],self.records[1]['capture_ref'])
        self.assertEqual(self.numeric['descriptor']['scale'],4096)
        for field in ('encoding','optimization','descriptor','selected_grid'):
            with self.subTest(field=field):
                bad=deepcopy(self.numeric);bad[field]={}
                with self.assertRaises(ValueError):q.check_numeric_v01(self.m,bad)
        wrong=deepcopy(self.m);wrong['profile']='MIX_CIRCLES_V01'
        with self.assertRaises(ValueError):q.check_numeric_v01(wrong,self.numeric)
        q.check_program_v01(self.m,self.numeric,self.program)

    def test_disclosure_and_request_zero_io_controls(self):
        bridge.check_request_v01(self.request,scope=self.scope,material=self.m,numeric=self.numeric,token=self.request['clientToken'])
        for key,value in (('runtime_arn','foreign'),('device_arn','foreign'),('bucket','foreign'),('structural_disclosure',False),('revoked',True),('shots',2000),('output_prefix','private/')):
            with self.subTest(field=key):
                bad=deepcopy(self.scope);bad[key]=value
                with self.assertRaises(ValueError):bridge.check_scope_v01(bad)
        for key,value in (('shots',999),('deviceArn','foreign'),('outputS3KeyPrefix','foreign/'),('private_name','PRIVATE_CANARY'),('tags',{'private':'x'})):
            with self.subTest(field=key):
                bad=deepcopy(self.request);bad[key]=value
                with self.assertRaises(ValueError):bridge.check_request_v01(bad,scope=self.scope,material=self.m,numeric=self.numeric,token=self.request['clientToken'])
        bad=deepcopy(self.request);wire=json.loads(bad['action']);wire['source']=wire['source'].replace('h q[0];','h q[1];');bad['action']=c.canonical(wire).decode()
        with self.assertRaises(ValueError):bridge.check_request_v01(bad,scope=self.scope,material=self.m,numeric=self.numeric,token=self.request['clientToken'])
        with self.assertRaises(ValueError):app.consume_v01(None,b'{}',self.arn,allow_suboptimal=True)

    def test_real_codec_columns_and_partial_records(self):
        a=q.samples_v01(self.m,self.numeric,c.canonical(self.raw),task_arn=self.arn)
        self.assertEqual(a['valid_samples'],1000);self.assertEqual(a['selected']['basis_index'],self.state)
        reordered=deepcopy(self.raw);reordered['measuredQubits'].reverse()
        reordered['measurements']=[list(reversed(row)) for row in reordered['measurements']]
        b=q.samples_v01(self.m,self.numeric,c.canonical(reordered),task_arn=self.arn)
        self.assertEqual(a['selected'],b['selected'])
        self.assertEqual(enc.measurement_index_v02([1,1,0,0,0,0,0,0,0,0],list(range(10))),3)
        self.assertEqual(enc.measurement_index_v02([0,0,0,0,0,0,0,0,1,1],list(reversed(range(10)))),3)
        for mutation in ('missing','extra','bool','short','duplicate_qubit','foreign_task'):
            with self.subTest(mutation=mutation):
                bad=deepcopy(self.raw)
                if mutation=='missing':bad['measurements'].pop()
                elif mutation=='extra':bad['measurements'].append(bad['measurements'][0])
                elif mutation=='bool':bad['measurements'][0][0]=True
                elif mutation=='short':bad['measurements'][0].pop()
                elif mutation=='duplicate_qubit':bad['measuredQubits'][0]=1
                else:bad['taskMetadata']['id']='foreign'
                with self.assertRaises(ValueError):q.samples_v01(self.m,self.numeric,c.canonical(bad),task_arn=self.arn)
        partial=deepcopy(self.raw);partial['measurements'].pop();partial['taskMetadata']['numSuccessfulShots']=999
        self.assertEqual(q.samples_v01(self.m,self.numeric,c.canonical(partial),task_arn=self.arn)['successful_shots'],999)
        none=deepcopy(self.raw);none['measurements']=[[1]*10]*1000
        self.assertEqual(q.samples_v01(self.m,self.numeric,c.canonical(none),task_arn=self.arn)['status'],'NO_VALID_PROVIDER_SAMPLE')

    def test_durable_slots_and_double_writer(self):
        with tempfile.TemporaryDirectory() as d:
            store=bridge.LedgerV01(d)
            with store.locked() as ledger:
                row=store.reserve(ledger,'KEEP',self.request,{'CONTROLLED':True})
                row['state']='SUBMISSION_OUTCOME_UNKNOWN';row['network_attempts']=1;store.save(ledger)
                with self.assertRaises(BlockingIOError):
                    with bridge.LedgerV01(d).locked():pass
            with bridge.LedgerV01(d).locked() as ledger:
                self.assertEqual(ledger['attempts'][0]['reserved_microusd'],725000)
                with self.assertRaises(ValueError):store.reserve(ledger,'KEEP',self.request,{})
                store.reserve(ledger,'MIX',dict(self.request,clientToken='SECOND'),{})
                with self.assertRaises(ValueError):store.reserve(ledger,'THIRD',dict(self.request,clientToken='THIRD'),{})
                self.assertEqual(sum(r['reserved_microusd'] for r in ledger['attempts']),1450000)

    def test_save_bytes_path_repeat_expiry(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d).resolve()/'seating.json';raw=b'{"controlled":true}'
            claim=dict(path=str(path),sha256=c.digest(raw),bytes=len(raw),expires=100)
            self.assertEqual(output.write_once_v01(claim,path,raw,99),'SAVED_READBACK_VERIFIED')
            self.assertEqual(output.write_once_v01(claim,path,raw,99),'ALREADY_SAVED_IDENTICAL')
            for target,body,now in ((path,b'{}',99),(Path(d).resolve()/'foreign',raw,99),(path,raw,100)):
                with self.assertRaises(ValueError):output.write_once_v01(claim,target,body,now)
            self.assertEqual(path.read_bytes(),raw)

    def test_actual_saved_clarification_no_search(self):
        from hedgehog.domains.wedding_seating import semantic_adapter_v01 as s
        i=json.loads((WORK/'basis_w3/story/AMBIGUOUS_intake.json').read_text())
        intake=s.LiveIntakeV01(self.original,self.original,i['request_ref'],i['safe_intent'],amendment_guests=tuple(i['amendment_guests']))
        records=json.loads((WORK/'basis_w3/story/AMBIGUOUS_captures.json').read_text())
        result=s.execute_live_v01(intake,records,now=1700000000,origin='CAPTURED_PROVIDER_RESPONSE_REEXECUTION')
        self.assertEqual(result['unresolved_ids'],['objective']);self.assertEqual(result['search_calls'],0)
        self.assertEqual(result['rendering_origin'],'LOCAL_RENDERING')
        self.assertIn('mix the circles',result['questions'][0])

if __name__=='__main__':unittest.main(verbosity=2)
