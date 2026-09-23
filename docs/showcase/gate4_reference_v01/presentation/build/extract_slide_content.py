"""Data-only extraction and editorial slide map. Never imports Radiolaria."""
import json, hashlib, os
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[2]
PRESENTATION=Path(__file__).resolve().parents[1]
STORY=Path(os.environ.get('G4_STORY_DIR',str(ROOT/'review/g44/portable_publication_final/story')))
if not STORY.exists():STORY=ROOT/'evidence/g44/portable_publication_final/story'
CONTENT=Path(os.environ.get('G4_CONTENT_DIR',str(PRESENTATION/'content')))
CONTENT.mkdir(parents=True,exist_ok=True)
OUT=CONTENT/'slide_text_and_notes_v01.json'
def load(f):return json.loads((STORY/f).read_text())
comparisons=load('comparisons.json')
rows=[];lane_data={}
for lane,profile in [('cold','PRICE_FIRST'),('contrast','COMFORT_FIRST'),('warm','PRICE_FIRST')]:
 a=load(lane+'/allocation_before_install.json');d=load(lane+'/domain_consumption.json');w=load(lane+'/completed_work.json')
 mapping={x['local_id']:x['native_id'] for x in a['basis']['mapping']}
 utilities={}
 for u in d['bridge']['strategy']['utilities']:utilities[(mapping[u['candidate_id']],mapping[u['root_id']])]=u['utility']
 if lane!='warm':
  for s in d['bridge']['strategy']['scores']:
   offer=mapping[s['id']]; us=[utilities[(offer,r)] for r in ['root:client_os_001','root:mock_airline_al','root:mock_bank_a']]
   rows.append([profile,offer.replace('g40:',''),*[f'{Decimal(u)/10**9:.3f}' for u in us],format(Decimal(s['product'])/Decimal(10**27),'f')])
 lane_data[lane]={'mapping':a['basis']['mapping'],'selected_offer':d['binding']['selected_offer_id'],'status':d['status'],'allocation_rows':a['allocation']['rows'],'output_binding':{k:v for k,v in w['output'].items() if k in ['allocation_identity','allocation_proof_sha256','original_basis_sha256']},'work_ids':comparisons['cp_budget'].get(lane+'_performed',[])}
refs={
1:['comparisons.json'],2:['comparisons.json'],3:['comparisons.json'],4:['comparisons.json','cold/domain_consumption.json','contrast/domain_consumption.json','cold/allocation_before_install.json','contrast/allocation_before_install.json'],5:['consent_cross_root_controls.json'],6:['comparisons.json','cold/allocation_before_install.json'],7:['observed_g3.json','history_recorded.json','warm/history_discovery.json'],8:['comparisons.json','cold/completed_work.json','warm/completed_work.json','cold/allocation_before_install.json','warm/allocation_before_install.json'],9:['cold/completed_work.json','cold/portable_records.json','cold/domain_consumption.json','cold/constructor_controls.json'],10:['current_expiry_controls.json','retained_history_current_controls.json','current_exhausted_budgets.json'],11:[],12:[]}
titles=[
'Gate 4\nReference',
'Mathematics participates in the operating architecture',
'Two valid offers express different interests',
'The declared preference changes the prepared offer',
'Each owner makes a current decision',
'Nine work units remain nine work units',
'An incorrect prediction becomes attributable experience',
'Experience changes which checks actually run',
'Allocated work reaches the final consumer',
'Current context remains binding',
'The saved result can be traced and checked',
'Reference accepted, deeper mathematics deferred']
leads=[
'Explicit trade-offs\nBounded work\nIndependent owners',
'G4 compares interests and allocates finite local Work. Each Root retains its decision.',
'Controlled Airline records share a EUR 840 ceiling, required baggage and no overnight layover.',
'Configured utility units and the finite Nash-product criterion yield different winners.',
'The recommendation remains offer:0 when Bank consent is missing.',
'One local task has a fixed cap of nine native Work dispatch units.',
'A controlled prediction is FALSE. The mandatory constraint check returns TRUE.',
'One source-bound sample changes the seven discretionary checks under PRICE_FIRST.',
'The native Work input carries the allocation proof. Its output binds the same allocation.',
'Valid old records remain subject to the original budget, expiry and current history checks.',
'Numerical references, recorded native work and supplied verification have distinct scopes.',
'Preferences change the prepared offer. Experience changes work allocation.']
claims=[['C01','C16'],['C01','C03'],['C02','C04','C05'],['C02','C04'],['C03'],['C07','C08'],['C06'],['C06','C07'],['C09','C12','C07','C08'],['C08','C10','C11','C05','C12'],['C13','C15'],['C01','C16']]
notes=[
'Owner-approved reduced mathematical scope. Implementation commit 5b259441994ba41ed3467e8ffcb9ae6ee8d371f0. Conceptual AI-generated Radiolaria artwork is not an evidence graph or cryptographic seal.',
'Conceptual architecture view. G3 contributes accepted outcome, local-memory and calibration mechanisms. Runtime owns finite enrolled Work. This native profile has max_children=0, max_model_calls=0. Three in-process sovereign Root reviews do not prove internet federation or legal agreement.',
'Controlled records, not a live airline catalogue. Legacy departure and return dates remain in originals. Utility disclosures are configured reference normalizations for client price margin and seat preference, airline revenue and bank budget margin. They are not EUR, probabilities or empirical happiness.',
'Both native candidates satisfy known hard predicates, individual rationality and Pareto filtering. D_i=0 and all alpha_i=1. Source fixed-point utility Q=10^9 and score denominator Q^3. Native integer reports determine ranking. This is finite reference bargaining, not Nash equilibrium or a fairness guarantee. No new live LLM calls.',
'Positive outcome PASS: Client, Airline and Bank ACCEPT. Removing the needed Bank consent produces Bank NEEDS_USER, overall MIXED and no domain continuation. Airline consent field is None in both lanes because its local admission requirements differ. Cross-root records carry evidence without transferred authority.',
'One unit is ONE_NATIVE_WORK_DISPATCH_UNIT. The local original cap is 9, spent=1, reserved mandatory final consumer=1 and available optional=7. Branch lower=2 upper=6. Catalogue has 12 possible optional quanta, seven execute. CPU time, money and token savings were not measured.',
'proposal_assessment=INCORRECT, enforcement_outcome=ALLOWED_AS_REQUIRED, execution_status=COMPLETED, task_outcome=COMPLETED. One native source-bound history sample, prior_fp=-62500000, effective_count=1, SPARSE. Warm names the presence of this sample, not a statistically robust population. No model retraining.',
'CP-BUDGET fixes domain records, hard constraints, branch features, quota limits, policy values, mandatory checks and PRICE_FIRST. Context IDs, current native time, Host revision, history descent and properly scoped consents may differ. Six checks remain common. The seventh is offer_0_4 in cold and offer_1_4 in warm, field price. Both lanes prepare offer0. Raw prior applies once. z_fp cold offer0=425000000 offer1=421250000, warm offer0=417187500 offer1=421250000.',
'Independently reconstructed original basis binds accepted allocation, revised Work literal, enrolled Host dispatch, completed output and final PURE consumer allocation-proof input. Its output binds allocation_identity, allocation_proof_sha256 and original basis. coherent_6_1 refuses with g4_reference:native_source_derived_budget before a changed executor. Original accepted allocation is its positive neighbour.',
'Current expiry just-before control prepares a result, at-boundary/after/future/rollback controls refuse. Retained history current descent has genuine accepted neighbours and refuses at/after the boundary. Current exhaustion retains original spending. Pure replay checks event-time relationships and does not renew authority today.',
'Recorded G41:110 pure-math tests. Recorded G43:26 nodes/78 phases, including17 native/history/preflight. G44 focused0017:33 PASS/1 FAIL,102 phases,45.056284s. Fail: mode test requested04644 but actual0644, accepted environment limitation. G44 Living19.888031s,Conformance19.903165s,G45 installed supplied19.859283s. Their complete1151634-byte outputs share SHA256136b2a76da196e42923886ffc5cf47d89e51d99ec8cc6c7ac549cfaea106b4b9. Named replay scope observes zero new model/collector/Host/Work/history-write/Root/effect/network calls,430 pure saved Root-result validations. SAFE_DERIVED_SAVED_RELATIONSHIPS_AT_RECORDED_EVENT_TIMES. Full native canonical replay UNSUPPORTED_NATIVE_SCHEMA. Trusted installed source and exact recorded checker environment required, including Python3.14.5,jsonschema4.26.0,referencing0.37.0 and executable identity. No universal clean-clone claim.',
'Reference engineering accepted / presentation prepared. Full Gate4 H-I-J after Gate6 publication remains for separate future scope decision. Deferred unilateral regret, stability,robust/minimax,CVaR,sensitivity,full AVF catalogue,richer priors and broader calibration. LGT excluded. No delivery date or automatic work implied. Versioned main paths are staged publication targets requiring repository access. Implementation commit is pinned; no future publication commit invented.'
]
slides=[]
for i in range(1,13):
 source=[]
 for f in refs[i]:
  p=STORY/f;source.append({'path':'evidence/g44/portable_publication_final/story/'+f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 slides.append({'number':i,'title':titles[i-1],'lead':leads[i-1],'claim_ids':claims[i-1],'source_label':' / '.join({3:['C02','C04'],9:['C09','C12'],10:['C08','C10','C11']}.get(i,claims[i-1])),'notes':{'explanation':notes[i-1],'sources':source,'implementation_commit':'5b259441994ba41ed3467e8ffcb9ae6ee8d371f0'}})
obj={'schema':'GATE4_PRESENTATION_CONTENT_V01','language':'English','units':{'utility':'Q=10^9','product':'Q^3=10^27','work':'ONE_NATIVE_WORK_DISPATCH_UNIT'},'strategy_rows':rows,'lane_data':lane_data,'comparisons':comparisons['cp_budget'],'slides':slides}
matrix=json.loads((CONTENT/'claim_evidence_matrix_v01.json').read_text())
claim_map={c['claim_id']:c for c in matrix['claims']}
for slide in obj['slides']:
 slide['notes']['claim_matrix_ref']='presentation/claim_evidence_matrix_v01.json'
 slide['notes']['claim_routes']=[claim_map[c] for c in slide['claim_ids']]
OUT.write_text(json.dumps(obj,indent=2)+'\n');print(OUT)
