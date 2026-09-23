"""Data-only authoring: read saved JSON and Python AST; never import project code."""
from pathlib import Path
import ast
import hashlib
import json
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
REVIEW = ROOT / 'gate4/review'
PIN = '5b259441994ba41ed3467e8ffcb9ae6ee8d371f0'
S = 'evidence/g44/portable_publication_final/story/'
P = 'evidence/g44/portable_publication_final/'
I = 'source_snapshot/installed/'

def local(path):
    for base in (OUT.parents[1], ROOT):
        capsule_member = base / path
        if capsule_member.is_file(): return capsule_member
    if path.startswith(I): return REVIEW / 'g45/postimages' / path[len(I):]
    return REVIEW / path.removeprefix('evidence/')

def read(path): return json.loads(local(path).read_text())
def digest(path): return hashlib.sha256(local(path).read_bytes()).hexdigest()
def pointer(obj, ptr):
    for key in ptr.split('/')[1:] if ptr else []:
        key = key.replace('~1','/').replace('~0','~')
        obj = obj[int(key)] if isinstance(obj,list) else obj[key]
    return obj
def data(path, ptr='', kind='RECORDED_CONTROLLED_NATIVE'):
    pointer(read(path), ptr)
    return dict(path=path,json_pointer=ptr,sha256=digest(path),evidence_class=kind)
def source(path, symbol=None, kind='ACTUAL_INSTALLED_SOURCE'):
    f=I+path
    if symbol:
        names={n.name for n in ast.walk(ast.parse(local(f).read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
        assert symbol in names, (f,symbol)
    return dict(path=f,symbol=symbol,sha256=digest(f),source_pin=PIN,evidence_class=kind)
def test(file,symbol):return source('tests/'+file+'.py',symbol,'TEST_LOCATOR_RECORDED_NOT_RUN_FOR_PRESENTATION')

comp=read(S+'comparisons.json')
facts=dict(Q=10**9,W=10**12,tau_fp=250000000,epsilon_gain_fp=1,alpha=1,rho=0,
           original_budget=comp['fixed']['policy_values'],comparison=comp,
           lanes={},scope='G4_REFERENCE_SCOPE_V01')
for lane in ('cold','contrast','warm'):
    a=read(S+lane+'/allocation_before_install.json');d=read(S+lane+'/domain_consumption.json');w=read(S+lane+'/completed_work.json')
    mapping={v['local_id']:v['native_id'] for v in a['basis']['mapping']}
    st=d['bridge']['strategy']
    rows=[]
    for score in st['scores']:
        cid=score['id']; us=[u for u in st['utilities'] if u['candidate_id']==cid]
        byroot={mapping[u['root_id']]:u['utility'] for u in us}
        rows.append(dict(offer_id=mapping[cid],candidate_id=cid,utility_fp=byroot,
                         product_integer=score['product'],display_product=str(Decimal(score['product'])/(Decimal(10)**27))))
    branches={q['branch']:q['offer_id'] for q in w['output']['consumed_quanta']}
    facts['lanes'][lane]=dict(profile=a['basis']['utility_profile'],mapping=a['basis']['mapping'],
       selected_offer=d['binding']['selected_offer_id'],status=d['status'],strategy_rows=rows,
       strategy_sets={k:st[k] for k in ('feasible','ir','pareto','ranking')},
       allocation_rows=[dict(x,offer_id=branches[x['id']]) for x in a['allocation']['rows']],
       budget=dict(total=a['budget']['total'],spent=a['budget']['spent'],reserved_mandatory=a['allocation']['mandatory_units'],available=a['allocation']['available'],unallocated=a['allocation']['unallocated']),
       actual_usage=w['after']['usage'],actual_attempt_count=len(w['attempts']),
       performed_ids=comp['cp_budget'].get(lane+'_performed'),
       final_ordered_work_ids=w['final']['program']['ordered_work_ids'],
       consumed_quanta=[{k:q[k] for k in ('offer_id','ordinal','field','checked_value','input_sha256','source_digest')} for q in w['output']['consumed_quanta']],
       consumer_output={k:v for k,v in w['output'].items() if k not in ('strategy_report','consumed_quanta')},
       current_decisions={r:v[2]['decision'] for r,v in d['current_reviews']['reviews'].items()},
       current_outcome=d['current_reviews']['outcome']['outcome_status'])
    assert len(st['feasible'])==len(st['ir'])==len(st['pareto'])==2
    assert w['after']['usage']['compute_units']==9 and w['after']['usage']['model_calls']==0
    assert len(w['output']['consumed_quanta'])==7
assert facts['lanes']['cold']['selected_offer']=='g40:offer:0'
assert facts['lanes']['contrast']['selected_offer']=='g40:offer:1'
assert facts['lanes']['warm']['selected_offer']=='g40:offer:0'
hist=read(S+'history_recorded.json')['snapshot']['prior'];obs=read(S+'observed_g3.json');cons=read(S+'consent_cross_root_controls.json')
facts['history_prior']={k:hist[k] for k in ('prior_fp','effective_count','sample_state','negative','positive','unresolved','profile')}
facts['observation']=dict(predicted=obs['claim']['payload']['predicted'],expected_fp=obs['claim']['payload']['expected_fp'],
   **{k:obs['feedback'][k] for k in ('proposal_assessment','enforcement_outcome','execution_status','task_outcome','blocking_stage','failure_class')})
facts['missing_consent']=dict(status=cons['missing_consent'],outcome=cons['mixed']['outcome']['outcome_status'],
    decisions={r:v[2]['decision'] for r,v in cons['mixed']['reviews'].items()},
    reasons={r:v[2]['reason_code'] for r,v in cons['mixed']['reviews'].items()},
    selected=cons['mixed']['selected'],permission_creation_count=cons['mixed']['outcome']['permission_creation_count'])
facts['checker_environment']=read(P+'MANIFEST.json')['checker_environment']
facts['retained_mode_diagnostic']=read('evidence/g44/commands/0019_filesystem_mode_diagnostic/mode_controls.json')

claims=[]
def claim(n,title,text,argument,section,slides,src,dat,tests=(),positive=(),negative=(),consumer=(),limits=()):
    claims.append(dict(claim_id=f'C{n:02}',title=title,claim=text,argument=argument,
       evidence_class='ACTUAL_SOURCE_AND_RECORDED_EVIDENCE',anchors=dict(slides=slides,appendix=section,reader=f'C{n:02}'),
       source_refs=list(src),data_refs=list(dat),test_refs=list(tests),positive_refs=list(positive),negative_refs=list(negative),consumer_refs=list(consumer),limits=list(limits)))

runtime='hedgehog/gate4_reference_runtime_v01.py'
adapter='hedgehog/domains/airline/gate4_reference_adapter_v01.py'
history='hedgehog/domains/airline/gate4_reference_history_v01.py'
evidence='hedgehog/gate4_reference_evidence_v01.py'
strategy='hedgehog/gate4_strategy_reference_v01.py'
pressure='hedgehog/gate4_pressure_budget_v01.py'
native_test='test_gate4_reference_native_v01';math_test='test_gate4_reference_math_v01';ev_test='test_gate4_reference_evidence_v01';hist_test='test_gate4_reference_history_v01'
claim(1,'Strategic comparison and actual bounded work','Gate 4 Reference adds finite multi-Root strategy comparison and bounded allocation of useful native work.','The strategy and allocation mechanisms enter actual Work results and local Root reviews, within the reduced contract.','a-result-scope-status',[1,2,12],
 [source('docs/gate4_reference_contract_v01.md'),source(strategy,'evaluate_reference_strategy_v01'),source(pressure,'allocate_reference_work_budget_v01')],
 [data(S+'comparisons.json')],[test(native_test,'test_native_causal_strategy_and_budget')],consumer=[data(S+'cold/completed_work.json','/output')],limits=['Full H-I-J mathematics and LGT remain deferred; no new model weights or authority.'])
claim(2,'Preference changes the prepared offer','PRICE_FIRST prepares offer0; COMFORT_FIRST prepares offer1.','Both reports rank the same two valid offers, then each selection is consumed by current reviews, resolution and a prepared hold.','g-cp-strategy',[3,4],
 [source(strategy,'evaluate_reference_strategy_v01'),source(adapter,'prepare_hold_v42')],
 [data(S+'comparisons.json','/cp_strategy'),data(S+'cold/allocation_before_install.json','/strategy_inputs'),data(S+'contrast/allocation_before_install.json','/strategy_inputs')],
 [test(native_test,'test_native_causal_strategy_and_budget')],positive=[data(S+'cold/domain_consumption.json','/binding'),data(S+'contrast/domain_consumption.json','/binding')],
 negative=[data(S+'native_supplied_controls.json','/coherent_changed_price')],consumer=[data(S+'cold/domain_consumption.json','/hold'),data(S+'contrast/domain_consumption.json','/hold')],limits=['PREPARATION_ONLY_NOT_EXECUTED; no booking, payment or seat reservation.'])
claim(3,'Each owner makes a current decision','Removing Bank consent leaves the recommendation but produces Bank NEEDS_USER and overall MIXED without hold continuation.','A valid arithmetic recommendation does not provide the missing local permission; Client and Airline remain separately ACCEPT.','g-cp-strategy',[5],
 [source(adapter,'strategy_reviews_v42')],[data(S+'consent_cross_root_controls.json','/missing_consent'),data(S+'consent_cross_root_controls.json','/mixed/outcome')],
 [test(native_test,'test_native_independent_consent_and_cross_root')],positive=[data(S+'consent_cross_root_controls.json','/positive')],negative=[data(S+'consent_cross_root_controls.json','/mixed/reviews/root:mock_bank_a/2'),data(S+'consent_cross_root_controls.json','/other_valid_offer')],consumer=[data(S+'cold/domain_consumption.json','/current_reviews')],limits=['Genuine in-process Root reviews and cross-root references; not proof of internet federation or legal agreement.'])
claim(4,'Exact finite ranking','Feasibility, IR, strict Pareto and equal-exponent integer products give an explainable finite recommendation.','Original integer utilities and products are retained; both native offers are feasible, IR and Pareto.','e-strategy-mathematics',[4],
 [source(strategy,'evaluate_reference_strategy_v01'),source(strategy,'validate_reference_strategy_report_v01')],
 [data(S+'cold/domain_consumption.json','/bridge/strategy'),data(S+'contrast/domain_consumption.json','/bridge/strategy')],
 [test(math_test,'test_strategy_fixed_sets_products_and_witness'),test(math_test,'test_epsilon_pareto_equal_vectors_and_single_final_round')],positive=[data(S+'cold/domain_consumption.json','/bridge/strategy/scores')],consumer=[data(S+'cold/completed_work.json','/output/strategy_report')],limits=['Configured utility units; not a probability, Nash equilibrium, incentive compatibility or universal fairness.'])
claim(5,'Suitability precedes ranking','Known hard-false cases are excluded before score allocation; missing required evidence does not become zero.','Strict contracts, explicit missing sets and report recomputation separate malformed, unknown and genuine no-deal outcomes.','e-strategy-mathematics',[3,10],
 [source(strategy,'evaluate_reference_strategy_v01'),source(pressure,'evaluate_reference_pressure_v01')],
 [data(S+'cold/domain_consumption.json','/bridge/strategy/exclusions')],
 [test(math_test,'test_strategy_dispositions'),test(math_test,'test_mask_before_softmax_negative_score_and_history_once')],positive=[data(S+'cold/domain_consumption.json','/bridge/strategy/feasible')],negative=[data(S+'native_supplied_controls.json','/evaluation_time')],limits=['Schema shape, arithmetic, contextual suitability and local permission remain separate checks.'])
claim(6,'Attributable experience changes one raw prior','One source-bound incorrect prediction yields prior -62500000, effective_count 1, SPARSE; the warm lane consumes it once.','The saved prospective claim, actual Work original, G3 feedback, independent recording review and current history descent bind the sample to the consumer.','h-cp-budget',[7,8],
 [source(history),source(evidence,'validate_observation_copies_v44'),source(evidence,'validate_history_subject_v44')],
 [data(S+'observed_g3.json','/claim/payload'),data(S+'observed_g3.json','/feedback'),data(S+'history_recorded.json','/snapshot/prior'),data(S+'warm/history_discovery.json')],
 [test(hist_test,'test_history_actual_native_proof_and_recording')],positive=[data(S+'history_recorded.json','/review')],negative=[data(S+'cold/constructor_controls.json','/controls/coherent_cold_prior/reason')],consumer=[data(S+'warm/allocation_before_install.json','/budget/pressure_inputs')],limits=['Warm names an available-history lane; its statistical sample state remains SPARSE. No model was called or trained.'])
claim(7,'History changes actual checks','Under the same PRICE_FIRST profile, allocations and performed optional checks change from 4/3 to 3/4.','The fourth price check moves from offer0 to offer1 and the final output lists the actual consumed quanta; offer0 remains selected.','h-cp-budget',[8,9],
 [source(pressure,'allocate_reference_work_budget_v01'),source(runtime,'NativeAllocationConsumerV01')],
 [data(S+'comparisons.json','/cp_budget'),data(S+'cold/allocation_before_install.json','/allocation/rows'),data(S+'warm/allocation_before_install.json','/allocation/rows')],
 [test(native_test,'test_native_causal_strategy_and_budget')],positive=[data(S+'cold/completed_work.json','/output/consumed_quanta'),data(S+'warm/completed_work.json','/output/consumed_quanta')],consumer=[data(S+'cold/completed_work.json','/final/program/ordered_work_ids'),data(S+'warm/completed_work.json','/final/program/ordered_work_ids')],limits=['Seven optional checks of a 12-check catalogue; no measured CPU, price or outcome-quality improvement.'])
claim(8,'Original spending is conserved','The 9-unit cap contains one already-spent initial check, seven optional checks and one reserved final consumer.','Budget reconstruction uses original policy and actual ledger usage; subsequent reports cannot reset cumulative spending.','f-pressure-allocation',[6,9],
 [source(adapter,'reconstruct_allocation_basis_v43'),source(pressure,'allocate_reference_work_budget_v01')],
 [data(S+'cold/enrolled.json'),data(S+'cold/allocation_before_install.json','/budget'),data(S+'cold/completed_work.json','/after/usage')],
 [test(native_test,'test_g43_new_consumer_original_budget_and_actual_proof'),test(native_test,'test_native_quota_refusals_and_real_exhaustion')],positive=[data(S+'cold/completed_work.json','/after/usage')],negative=[data(S+'cold/completed_work.json','/controls/stale_spending_revision'),data(S+'current_exhausted_budgets.json')],consumer=[data(S+'cold/completed_work.json','/controls/terminal_retry')],limits=['ONE_NATIVE_WORK_DISPATCH_UNIT measures admitted dispatches, not time, tokens, money or FLOPs.'])
claim(9,'Allocated results reach the final consumer','The actual final PURE consumer receives allocation proof and produces an output bound to allocation identity, proof digest and original basis.','Explicit Work literals and completed results connect the allocation to downstream strategy and hold preparation.','h-cp-budget',[9],
 [source(adapter,'validate_allocation_proof_v43'),source(adapter,'strategy_work_result_v42')],
 [data(S+'cold/completed_work.json','/output'),data(S+'warm/completed_work.json','/output'),data(S+'cold/portable_records.json','/final_program')],
 [test(native_test,'test_g43_new_consumer_original_budget_and_actual_proof')],positive=[data(S+'cold/completed_work.json','/output/allocation_proof_sha256')],negative=[data('evidence/g44/commands/0017_final_focused/proof_controls/negative_result.json','/reason','RECORDED_SAVED_PROOF_CONTROL')],consumer=[data(S+'cold/domain_consumption.json','/bridge/work_artifact')],limits=['Acyclic proof/material dependency; no independent authority is created by the output.'])
claim(10,'Original validity is not renewed','Current consumers check original source expiry even when reviews or wrappers are fresh.','Just-before-expiry preparation is retained alongside boundary/after/future/rollback refusals and a separate shorter-offer task.','j-currentness-replay',[10],
 [source(adapter,'current_use_v43')],[data(S+'current_expiry_controls.json'),data(S+'short_offer/shorter_offer_control.json')],
 [test(native_test,'test_g43_current_expiry_actual_consumers'),test(native_test,'test_g43_shorter_offer_ttl')],positive=[data(S+'current_expiry_controls.json','/just_before/status')],negative=[data(S+'current_expiry_controls.json','/at_boundary'),data(S+'current_expiry_controls.json','/rollback')],consumer=[data(S+'cold/current_use.json')],limits=['Saved current-at-event-time suitability does not restore current permission today.'])
claim(11,'Retained history must qualify again','A previously valid history opening is not blindly reusable after time advances.','The warm lane performs current Root-approved descent and rejects invalid current history while preserving the enrolled basis and usage.','j-currentness-replay',[10],
 [source(history)],[data(S+'retained_history_current_controls.json')],[test(hist_test,'test_g43_retained_history_current_requalification')],
 positive=[data(S+'retained_history_current_controls.json','/current_descent')],negative=[data(S+'retained_history_current_controls.json','/at_boundary')],consumer=[data(S+'warm/current_history.json')],limits=['History eligibility is narrower than physical truth; the trusted local memory boundary is explicit.'])
claim(12,'Coherent false relations are rejected','Resealing a wrong quota, prior, result, root or offer relation does not make it admissible.','The verifier compares against independent original basis and source relations after outer integrity has been rebuilt.','i-boundary-controls',[9,10],
 [source(adapter,'reconstruct_allocation_basis_v43'),source(evidence,'validate_saved_story_v01')],
 [data(S+'cold/constructor_controls.json','/controls'),data('evidence/g44/commands/0018_final_parent_controls/controls.json','','RECORDED_PARENT_CONTROL')],
 [test(ev_test,'test_g43_semantic_controls_with_resealed_test_pin'),test(native_test,'test_native_source_and_coherent_supplied_controls')],
 positive=[data(S+'cold/allocation_before_install.json','/allocation/rows'),data('evidence/g44/commands/0017_final_focused/proof_controls/supported_result.json','','RECORDED_SAVED_PROOF')],
 negative=[data('evidence/g44/commands/0017_final_focused/proof_controls/negative_'+c+'.json','/reason','RECORDED_SAVED_PROOF_CONTROL') for c in ('quota','prior','result','root','offer')],consumer=[data(S+'cold/completed_work.json','/output')],limits=['Refusals occur at named constructor/currentness/saved-relation boundaries; they are not all Firewall blocks.'])
claim(13,'The checker is independently installed','Saved evidence cannot choose the checker implementation or substitute a transitive source body.','G44 P1 checks actual import origins, finite checker closure and exact recorded environment before saved semantics; archived source bodies remain inert.','j-currentness-replay',[11],
 [source(evidence,'checker_sources_v44'),source(evidence,'checker_environment_v44')],
 [data(P+'MANIFEST.json','/checker_source_ledger','RECORDED_CHECKER_PROVENANCE'),data(P+'MANIFEST.json','/producer_source_ledger','RECORDED_PRODUCER_PROVENANCE'),data(P+'MANIFEST.json','/checker_environment','RECORDED_CHECKER_ENVIRONMENT')],
 [test(ev_test,'test_g44_missing_checker_dependency_refuses'),test(ev_test,'test_g44_preloaded_alternative_origin_core_mismatch_refuses')],
 positive=[data('evidence/g45/installed_supplied/combined.json','/status','RECORDED_INSTALLED_SUPPLIED')],limits=['Requires a matching trusted environment; not an arbitrary clean-clone replay promise or hostile same-UID process containment.'])
claim(14,'A genuine approval can have the wrong subject','A real same-Root recording ACCEPT for another subject cannot authorize this history snapshot.','G44 P2 binds copied claim/result material to cold originals; P3 binds recording input, transaction, subject and meaning references.','i-boundary-controls',[],
 [source(evidence,'validate_observation_copies_v44'),source(evidence,'validate_history_subject_v44')],
 [data(S+'history_recorded.json','/review'),data(S+'observed_g3.json','/claim')],
 [test(ev_test,'test_g44_history_same_root_other_genuine_subject_refuses')],
 positive=[data(S+'history_recorded.json','/root_records')],negative=[data('evidence/g44/commands/0017_final_focused/proof_controls/negative_claim_copy.json','/reason','RECORDED_SAVED_PROOF_CONTROL'),data('evidence/g44/commands/0017_final_focused/proof_controls/negative_native_copy.json','/reason','RECORDED_SAVED_PROOF_CONTROL')],consumer=[data(S+'warm/history_discovery.json')],limits=['Subject-specific evidence; a genuine signature or ACCEPT is not universal approval.'])
claim(15,'Saved verification is deterministic without new authority','G44 Living, G44 Conformance and G45 installed supplied checks produced identical 1,151,634-byte canonical outputs.','Equal whole-file SHA256 and the named counters support deterministic saved relationship checks without new native execution.','k-verification-inventory',[11],
 [source(evidence,'verify_package_v01')],
 [data('evidence/g44/commands/0020_supplied_living_final/combined.json','','RECORDED_SUPPLIED_LIVING'),data('evidence/g44/commands/0021_supplied_conformance_final/combined.json','','RECORDED_SUPPLIED_CONFORMANCE'),data('evidence/g45/installed_supplied/combined.json','','RECORDED_INSTALLED_SUPPLIED')],
 [test(ev_test,'test_g43_saved_positive_and_test_pin')],limits=['SAFE_DERIVED_SAVED_RELATIONSHIPS_AT_RECORDED_EVENT_TIMES; full native canonical replay is UNSUPPORTED_NATIVE_SCHEMA. Named monitoring is not OS-wide surveillance.'])
claim(16,'Installation and presentation are separate','G45 landed the reviewed implementation at the pinned commit; presentation publication has a separate identity and review.','The installation report and result retain actual commit/parent/tree; historical NOT_CLOSED and TEST_SUPPLIED_PIN labels remain unchanged.','a-result-scope-status',[1,12],
 [source('docs/gate4_reference_release_checkpoint_v01.md')],[data('evidence/g45/RESULT.json','','RECORDED_OWNER_LANDING')],limits=['Unsigned Git commit is not an external audit signature. No future publication hash is invented.'])

matrix=dict(schema_version='G4_PRESENTATION_CLAIM_EVIDENCE_MAP_V01',identity=dict(implementation_commit=PIN,created_date='2026-09-23',authoring_only=True),
scope='G4_REFERENCE_SCOPE_V01',provenance_rules=dict(specification_intent='The implementation master is a design source, not runtime evidence; its fixture vectors are NUMERICAL_REFERENCE_NOT_RUNTIME.',actual_source='source_snapshot/installed contains G45 landed postimages, byte-equal to reviewed G44 postimages.',recorded_native='G43 source-bound controlled native story retained in G44; no new native execution for presentation.',current_checker='G44 checker closure and G45 installed supplied result are separate from recorded producer source.',schema_limit='Pointer and schema checks validate shape/navigation; semantic and contextual obligations require their named validators.'),
numerical_facts=facts,claims=claims)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'claim_evidence_matrix_v01.json').write_text(json.dumps(matrix,indent=2,ensure_ascii=True)+'\n')
print('Wrote',len(claims),'claims with verified paths, JSON pointers, hashes and AST source/test locators.')
