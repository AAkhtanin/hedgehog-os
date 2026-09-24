#!/usr/bin/env python3
"""Independent bytes-only parser/security check. No archived code imports."""
import base64, collections, hashlib, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
j=lambda p:json.loads(p.read_text())
mapping=j(P/'evidence/SOURCE_MAP.json')['source_records']
refs={r['source_id']:r for r in mapping}
lookup={(r['source_archive'],r['original_member']):r for r in mapping}
raw=lambda r:(P/r['storage_path']).read_bytes()
errors=[];checked=0
for r in mapping:
 b=raw(r);checked+=1
 if sha(b)!=r['raw_sha256'] or len(b)!=r['bytes']:errors.append('source:'+r['source_id'])
for r in mapping:
 manifest=lookup[(r['source_archive'],'MANIFEST.json')]
 assert sha(raw(manifest))==r['original_manifest_sha256']
 if r['original_manifest_row_verified']:
  rows={row['path']:row for row in json.loads(raw(manifest))['files']}
  assert rows[r['original_member']]['sha256']==r['raw_sha256']
  assert rows[r['original_member']]['bytes']==r['bytes']
x=(P/'WEDDING_LLM_READER_V01.xml').read_bytes()
assert b'<!DOCTYPE' not in x and b'<!ENTITY' not in x,'DTD/entity forbidden'
root=ET.fromstring(x)
blobs={}
for e in root.findall('.//full_raw_source'):
 b=base64.b64decode(e.text) if e.get('encoding')=='base64' else (e.text or '').encode()
 if sha(b)!=e.get('sha256') or len(b)!=int(e.get('bytes')):errors.append('XML raw:'+e.get('id'))
 blobs[e.get('sha256')]=b
for e in root.findall('.//source_ref'):
 if e.get('source_id') not in refs:errors.append('missing reference:'+e.get('source_id'))
projection_count=0
for e in root.findall('.//selected_projection'):
 rec=refs[e.get('source_id')];obj=json.loads(raw(rec))
 assert e.get('source_raw_sha256')==rec['raw_sha256']
 for part in e.get('json_pointer').strip('/').split('/'):
  part=part.replace('~1','/').replace('~0','~');obj=obj[int(part)] if isinstance(obj,list) else obj[part]
 rendered=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 assert rendered==(e.text or '').encode() and sha(rendered)==e.get('projection_sha256')
 projection_count+=1
status=collections.Counter();response_rows=[];original_captures={}
for i in range(1,20):
 key=f'captures/attempt_{i:03d}/'
 rs={n:lookup[('W3',key+n)] for n in ['request_body.json','response.txt','capture.json','receipt.json','provider_response.json','destination.json']}
 for r in rs.values():
  if blobs.get(r['raw_sha256'])!=raw(r):errors.append('call not full:'+r['source_id'])
 cap=json.loads(raw(rs['capture.json']));receipt=json.loads(raw(rs['receipt.json']));provider=json.loads(raw(rs['provider_response.json']));destination=json.loads(raw(rs['destination.json']))
 text=''.join(part.get('text') or '' for candidate in provider['candidates'] for part in candidate['content']['parts'])
 assert text.encode()==raw(rs['response.txt'])==cap['raw_response'].encode()
 assert cap['request_body'].encode()==raw(rs['request_body.json'])
 assert destination==cap['egress'] and destination['query']==''
 assert cap['response_sha256']==rs['response.txt']['raw_sha256']
 status[receipt['status']]+=1
 assert receipt['wire_sends']==1
 original_captures[cap['capture_ref']]={'attempt':i,'capture':cap,'receipt':receipt}
 response_rows.append({'attempt':i,'raw_response_sha256':rs['response.txt']['raw_sha256'],'provider_text_exact':True,'capture_text_exact':True,'request_exact':True,'destination_exact':True})
final_captures=[]
for episode in ['A','B','AMBIGUOUS','VERIFY','SR1','SR2','SR3']:
 rec=lookup[('W5','portable/w3/story/'+episode+'_captures.json')]
 for capture in json.loads(raw(rec)):
  origin=original_captures[capture['capture_ref']]
  assert all(capture[k]==origin['capture'][k] for k in ['raw_response','request_body','response_sha256','request_ref','role'])
  final_captures.append({'episode':episode,'attempt':origin['attempt'],'initial_status':origin['receipt']['status'],'capture_ref':capture['capture_ref'],'raw_request_response_unchanged':True})
assert len(final_captures)==14 and len({r['capture_ref'] for r in final_captures})==14
assert any(r['attempt']==15 and r['episode']=='SR1' and r['initial_status']=='FAILED' for r in final_captures)
code=j(P/'evidence/CODE_MAP.json')['snapshots']
assert len(code)==34
for r in code:assert blobs[r['raw_sha256']]==(P/r['storage_path']).read_bytes()
hardware_rows=[]
for profile,expected in [('KEEP_FAMILIAR_V01',(33,16,5,63)),('MIX_CIRCLES_V01',(42,20,18,31))]:
 p=P/'evidence/portable/w4';rpath=p/f'provider/{profile}_results.json';result=j(rpath)
 validation=j(p/f'provider/{profile}_sample_validation.json');saved=j(p/f'outputs/{profile}/seating.json');native=j(p/f'native/{profile}/consume.json')
 assert sha(rpath.read_bytes())==validation['raw_sha256']==saved['raw_sha256']
 assert len(result['measurements'])==len(validation['lineage'])==validation['successful_shots']==1000
 for i,(shot,line) in enumerate(zip(result['measurements'],validation['lineage'])):
  assert i==line['shot_index'] and sum(bit<<q for bit,q in zip(shot,result['measuredQubits']))==line['basis_index']
 valid=[line for line in validation['lineage'] if line['status']=='VALID']
 distinct=len({tuple(line['assignment']) for line in valid})
 best=sum(line['validation']['components']['objective']==validation['local_reference_objective'] for line in valid)
 assert (len(valid),distinct,best,saved['shot_index'])==expected
 assert saved==native['output']
 assert all(saved[k]==validation['selected'][k] for k in ['assignment','basis_index','shot_index'])
 assert native['root_result']['decision']=='ACCEPT' and saved['local_repair'] is False
 hardware_rows.append({'profile':profile,'measurements':1000,'valid':len(valid),'distinct_valid':distinct,'recorded_best_objective_shots':best,'selected_shot_index':saved['shot_index'],'raw_bits_to_recorded_basis_all_1000_exact':True,'saved_equals_native_output':True,'scope':'SAVED_RELATION_CONSISTENCY_NO_VALIDATOR_OR_SOLVER_RERUN'})
scan_patterns={
 'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
 'aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'google_api_key':rb'\bAIza[0-9A-Za-z_-]{30,}\b',
 'openai_key':rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b',
 'github_token':rb'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{30,}\b',
 'bearer_token':rb'(?i)authorization["\s:=]+bearer\s+[a-z0-9._~-]{20,}',
 'signed_aws_url':rb'(?i)(?:X-Amz-Signature|X-Amz-Credential)=[^&\s"<>]{12,}',
 'nonempty_secret_json_field':rb'(?i)"(?:api_key|secret_access_key|aws_secret_access_key|access_token|refresh_token|client_secret|authorization)"\s*:\s*"(?!REDACTED|redacted|<|\*|"|null|None)[^"\r\n]{12,}"',
}
findings=[];scanned=[]
for p in sorted(P.rglob('*')):
 if not p.is_file():continue
 b=p.read_bytes();scanned.append({'path':str(p.relative_to(P)),'sha256':sha(b),'bytes':len(b)})
 # All current evidence formats are text; binary exports are recorded but not interpreted.
 for label,pat in scan_patterns.items():
  for m in re.finditer(pat,b):findings.append({'path':str(p.relative_to(P)),'rule':label,'offset':m.start(),'match_sha256':sha(m.group()),'matched_value_omitted':True})
report={'schema':'WeddingIndependentReaderValidationV01','status':'PASS' if not errors and not findings else 'REVIEW_REQUIRED',
 'checked_source_identities':checked,'source_identity_errors':errors,'all_19_raw_provider_capture_request_destination_consistent':True,
 'initial_status_counts':dict(status),'response_rows':response_rows,'code_snapshots_full_and_exact':34,
 'final_capture_identity_rows':final_captures,'final_capture_raw_fields_unchanged':True,
 'xml_bytes':len(x),'xml_sha256':sha(x),'xml_full_blob_count':len(blobs),'xml_dtd_entities_absent':True,
 'original_manifest_rows_verified':True,'exact_json_pointer_projections':projection_count,'hardware_saved_relation_consistency':hardware_rows,
 'security_scan_rules':list(scan_patterns),'high_confidence_secret_findings':findings,
 'security_scan_limit':'Pattern-based content scan; hash identities and original privacy/source classifications retained. Binary presentation exports need their own link/content checks.',
 'scanned_files':scanned,'python_version':sys.version,'archived_code_executed':False,'network_calls':0}
# Read-only: report is printed; no files are modified.
print(json.dumps({k:v for k,v in report.items() if k not in ['scanned_files','response_rows','final_capture_identity_rows']},indent=2))
raise SystemExit(0 if report['status']=='PASS' else 1)
