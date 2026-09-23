"""Pure independent oracles. No native fixtures or runtime producers."""
from copy import deepcopy
from decimal import Context, Decimal, ROUND_DOWN, ROUND_HALF_EVEN, getcontext, localcontext
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import random

import pytest
from hedgehog.gate4_reference_contracts_v01 import (
    Q, W, TAU, G4_REFERENCE_NUMERIC_V01 as PROFILE, ReferenceValueV01, checked, digest,
)
from hedgehog.gate4_strategy_reference_v01 import evaluate_reference_strategy_v01 as strategy
from hedgehog.gate4_pressure_budget_v01 import (
    evaluate_reference_pressure_v01 as pressure, allocate_reference_work_budget_v01 as allocate,
    _apportion, _weights,
)
from hedgehog.outcome_calibration_v01 import round_half_even_rational_v01 as rhe

FIXTURE = Path(__file__).parents[1]/'fixtures/gate4_reference_math_v01.json'


def fixture():
    return json.loads(FIXTURE.read_bytes())


def seal_strategy(data):
    """Construct independent reference input pins, never expected outputs."""
    data = deepcopy(data)
    for c in data['candidates']:
        normalized = checked('candidate',c)
        c['source_hash'] = digest({k:v for k,v in normalized.items() if k != 'source_hash'})
    d = checked('strategy_input',data)
    d['context']['candidate_set_hash'] = digest(d['candidates'])
    d['context']['source_snapshot_hash'] = digest({k:d[k] for k in ('candidates','disagreements')})
    return d


def seal_budget(data):
    """A new separately configured numerical reference, not native currentness."""
    data = deepcopy(data)
    p = checked('pressure_input',data['pressure_inputs'])
    ctx = data['context']
    ctx['candidate_set_hash'] = digest([b['id'] for b in p['branches']])
    ctx['source_snapshot_hash'] = digest(p['branches'])
    ctx['policy_hash'] = digest(dict(total=data['total'],policy_ref=ctx['policy_ref'],owner_root_id=ctx['owner_root_id'],task_id=ctx['task_id']))
    data['original_policy_hash'] = ctx['policy_hash']
    data['spending_snapshot_hash'] = digest({k:data[k] for k in ('spent','host_revision')} |
        {k:ctx[k] for k in ('owner_root_id','task_id','transaction_id')})
    p['context'] = deepcopy(ctx); data['pressure_inputs'] = p
    return checked('budget',data)


def run_strategy(d):
    d = seal_strategy(d)
    return strategy(d,independently_bound_context=deepcopy(d['context'])).plain()


def run_budget(b):
    b = seal_budget(b)
    p = pressure(b['pressure_inputs'],profile=PROFILE)
    return allocate(p,current_budget_context=b).plain()


def nearest_oracle(n,d):
    x = Fraction(n,d)
    a = x.numerator//x.denominator
    return min((a,a+1), key=lambda k:(abs(x-k),k%2))


def allocation_oracle(a, lower, upper, weights):
    """Enumerate saturated sets to solve the water level, not the production loop."""
    n = len(lower); target = min(a,sum(upper)); excess = target-sum(lower)
    if excess < 0: raise ValueError('minima')
    capacities = [u-l for l,u in zip(lower,upper)]
    extras = None
    for count in range(n+1):
        for selected in combinations(range(n),count):
            fixed = set(selected); active = [i for i in range(n) if i not in fixed]
            rest = excess-sum(capacities[i] for i in fixed)
            if rest < 0: continue
            if not active:
                if rest == 0: extras = list(map(Fraction,capacities))
                continue
            level = Fraction(rest,sum(weights[i] for i in active))
            if all(level*weights[i] >= capacities[i] for i in fixed) and all(level*weights[i] <= capacities[i] for i in active):
                extras = [Fraction(capacities[i]) if i in fixed else level*weights[i] for i in range(n)]
    assert extras is not None
    floors = [x.numerator//x.denominator for x in extras]
    left = excess-sum(floors)
    # Independently maximize the total selected fractional residual.
    eligible = [i for i in range(n) if floors[i] < capacities[i]]
    choices = list(combinations(eligible,left))
    choice = min(choices,key=lambda s:(-sum(extras[i]-floors[i] for i in s),s))
    return [lower[i]+floors[i]+(i in choice) for i in range(n)], a-target


@pytest.mark.parametrize('n,d',[(1,2),(3,2),(5,2),(-1,2),(-3,2),(-5,2),(7,3),(-7,3),(10**30+5,10)])
def test_signed_exact_rounding(n,d):
    assert rhe(n,d) == nearest_oracle(n,d)


def test_strategy_fixed_sets_products_and_witness():
    r = run_strategy(fixture()['strategy'])
    ids = lambda names:['g4_reference:candidate:'+n for n in names]
    assert r['ir'] == ids('ABC') and r['pareto'] == ids('AB') and r['recommendation'] == ids('B')[0]
    assert {s['id']:s['product'] for s in r['scores']}[ids('A')[0]] == '45000000000000000000000000'
    assert {s['id']:s['product'] for s in r['scores']}[ids('B')[0]] == '125000000000000000000000000'
    assert r['witnesses'][0]['dominator'] == ids('B')[0]
    assert all(x['delta'] == 100000000 for x in r['witnesses'][0]['differences'])
    assert len(r['failed_comparisons']) == 1 and r['root_review_required'] and not r['creates_permission']
    assert all(v['status'] == 'NOT_IMPLEMENTED' for v in r['deferred'].values())


@pytest.mark.parametrize('case,status',[('below','NO_DEAL_BELOW_DISAGREEMENT'),('zero','NO_DEAL_ALL_ZERO_GAIN'),
    ('false','NO_DEAL_NO_FEASIBLE'),('hard_unknown','NEEDS_MORE_EVIDENCE'),('missing_u','NEEDS_MORE_EVIDENCE'),
    ('missing_d','NEEDS_MORE_EVIDENCE'),('expired','NEEDS_MORE_EVIDENCE'),('uncertain','NEEDS_MORE_EVIDENCE')])
def test_strategy_dispositions(case,status):
    d = fixture()['strategy']
    if case == 'below': d['disagreements'][1]['value'] = 600000000
    if case == 'zero':
        for c in d['candidates']:
            for u in c['utilities']: u['terms'][0]['feature_fp'] = 0
    if case == 'false':
        for c in d['candidates']: c['hard'][0]['state'] = 'FALSE'; c['utilities'] = []
    if case == 'hard_unknown': d['candidates'][0]['hard'][0]['state'] = 'UNKNOWN'
    if case == 'missing_u': d['candidates'][0]['utilities'].pop()
    if case == 'missing_d': d['disagreements'][0].update(value=None,validity='MISSING')
    if case == 'expired': d['candidates'][0]['utilities'][0]['validity'] = 'EXPIRED'
    if case == 'uncertain': d['candidates'][0]['utilities'][0]['uncertainty'] = 'UNKNOWN'
    r = run_strategy(d)
    assert r['status'] == status and r['recommendation'] is None


def test_hard_false_before_unknown_and_invalid_excluded_source():
    d = fixture()['strategy']; c = d['candidates'][1]
    c['hard'][0]['state'] = 'FALSE'; c['utilities'] = []
    c['hard'].append(dict(id='g4_reference:hard:unknown',state='UNKNOWN',evidence_ref='g4_reference:evidence:unknown'))
    d = seal_strategy(d)
    r = strategy(d,independently_bound_context=d['context']).plain()
    assert r['status'] == 'RECOMMENDATION' and c['id'] not in r['feasible']
    d['candidates'][1]['source_hash'] = 'f'*64
    d['context']['candidate_set_hash'] = digest(d['candidates'])
    d['context']['source_snapshot_hash'] = digest({k:d[k] for k in ('candidates','disagreements')})
    with pytest.raises(ValueError,match='candidate_source'): strategy(d,independently_bound_context=d['context'])


def test_epsilon_pareto_equal_vectors_and_single_final_round():
    d = fixture()['strategy']; d['candidates'] = d['candidates'][:2]
    d['context']['participants'] = d['context']['participants'][:2]; d['disagreements'] = d['disagreements'][:2]
    for c,name,values in zip(d['candidates'],['a','z'],[(0,1),(1,1)]):
        c['id'] = 'g4_reference:candidate:'+name
        c['participants'] = c['required_roots'] = d['context']['participants'][:]
        c['utilities'] = c['utilities'][:2]
        for u,x in zip(c['utilities'],values): u['candidate_id'] = c['id']; u['terms'][0]['feature_fp'] = x
    r = run_strategy(d)
    assert r['recommendation'].endswith(':z') and r['pareto'] == [r['recommendation']]
    assert [s['product'] for s in r['scores']] == ['1','1']
    d['candidates'][0]['utilities'][0]['terms'][0]['feature_fp'] = 1
    assert len(run_strategy(d)['pareto']) == 2
    for c in d['candidates']:
        for u in c['utilities']:
            t = u['terms'][0]; t['weight_fp'] = Q//2
            t2 = deepcopy(t); t2['id'] = 'g4_reference:term:2'; u['terms'].append(t2)
    assert all(t['weighted'] == 1 for t in run_strategy(d)['utilities'])


def test_max_product_and_seeded_independent_strategy_oracle():
    d = fixture()['strategy']; rng = random.Random(41012026)
    for _ in range(24):
        vectors = {c['id']:[rng.randrange(-3,6)*100000000 for _ in range(3)] for c in d['candidates']}
        for c in d['candidates']:
            for u,x in zip(c['utilities'],vectors[c['id']]): u['terms'][0]['feature_fp'] = x
        r = run_strategy(d); ir = sorted(k for k,v in vectors.items() if min(v)>=0)
        p = [k for k in ir if not any(all(a>=b for a,b in zip(vectors[j],vectors[k])) and vectors[j]!=vectors[k] for j in ir)]
        assert r['ir'] == ir and r['pareto'] == p
        if p:
            def product(k):
                x,y,z = vectors[k]; return max(x,1)*max(y,1)*max(z,1)
            assert r['recommendation'] == min(p,key=lambda k:(-product(k),k))
    roots=['g4_reference:root:'+str(i) for i in range(8)]
    d=fixture()['strategy']; d['context']['participants']=roots; d['context']['owner_root_id']=roots[0]
    template=deepcopy(d['disagreements'][0]); d['disagreements']=[dict(template,root_id=r,value=-4*Q) for r in roots]
    for c in d['candidates']:
        u=deepcopy(c['utilities'][0]); u['terms'][0]['feature_fp']=Q
        c['participants']=c['required_roots']=roots[:]; c['utilities']=[dict(deepcopy(u),root_id=r) for r in roots]
    result=run_strategy(d)
    assert all(s['product']==str((5*Q)**8) and len(s['product'])<=80 for s in result['scores'])


@pytest.mark.parametrize('prior,z,weights,allocation',[(0,[425000000,421250000],[1000000000000,985111939603],[4,3]),
    (-62500000,[417187500,421250000],[983881318977,1000000000000],[3,4])])
def test_pressure_contrast(prior,z,weights,allocation):
    b = fixture()['budget']; b['pressure_inputs']['branches'][0]['prior'].update(value=prior,disposition='USABLE')
    r = run_budget(b)
    assert [x['z_fp'] for x in r['rows']] == z
    assert [x['weight'] for x in r['rows']] == weights
    assert [x['allocation'] for x in r['rows']] == allocation and r['mandatory_units']+sum(allocation) == 9
    with localcontext(Context(prec=160,rounding=ROUND_HALF_EVEN,Emin=-999999,Emax=999999,capitals=1,clamp=0,flags=[],traps=[])):
        assert weights == [int((Decimal(W)*((Decimal(v)-max(z))/Decimal(TAU)).exp()).to_integral_value()) for v in z]


@pytest.mark.parametrize('index',range(6))
def test_hand_allocation_vectors(index):
    a,l,u,w,expected,left = fixture()['allocation_vectors'][index]
    ids=['g4_reference:b'+str(i) for i in range(len(l))]
    if expected is None:
        with pytest.raises(ValueError,match='infeasible_minima'): _apportion(a,dict(zip(ids,l)),dict(zip(ids,u)),dict(zip(ids,w)))
    else:
        r = _apportion(a,dict(zip(ids,l)),dict(zip(ids,u)),dict(zip(ids,w)))
        assert list(r['allocations'].values()) == expected and r['unallocated'] == left
        assert allocation_oracle(a,l,u,w) == (expected,left)


def test_seeded_allocation_by_saturated_set_enumeration():
    rng=random.Random(41012026)
    for _ in range(96):
        n=rng.randrange(1,6); l=[rng.randrange(3) for _ in range(n)]; u=[x+rng.randrange(5) for x in l]
        w=[rng.randrange(1,9) for _ in range(n)]; a=sum(l)+rng.randrange(13)
        ids=['g4_reference:b'+str(i) for i in range(n)]
        r=_apportion(a,dict(zip(ids,l)),dict(zip(ids,u)),dict(zip(ids,w)))
        assert (list(r['allocations'].values()),r['unallocated']) == allocation_oracle(a,l,u,w)


@pytest.mark.parametrize('case,status',[('excluded','ALLOCATED'),('zero_caps','ALLOCATED'),('zero_a','ALLOCATED'),
    ('mandatory','BUDGET_INSUFFICIENT'),('minima','INFEASIBLE_MINIMA'),('unknown','NEEDS_MORE_EVIDENCE')])
def test_budget_boundaries(case,status):
    b=fixture()['budget']; branches=b['pressure_inputs']['branches']
    if case=='excluded':
        for v in branches: v['hard'][0]['state']='FALSE'
    if case=='zero_caps':
        for v in branches: v.update(lower=0,upper=0)
    if case=='zero_a':
        b['total']=2
        for v in branches: v['lower']=0
    if case=='mandatory': b['total']=1
    if case=='minima': b['total']=5
    if case=='unknown': branches[0]['available']='UNKNOWN'
    r=run_budget(b); assert r['status']==status
    if status!='ALLOCATED': assert not r['rows'] and not r['rounds']
    elif case=='excluded': assert not r['rows'] and r['unallocated']==7
    else: assert all(x['allocation']==0 for x in r['rows'])


def test_mask_before_softmax_negative_score_and_history_once():
    b=fixture()['budget']; a,c=b['pressure_inputs']['branches']; a['hard'][0]['state']='FALSE'
    for k in ('relevance','lineage'): c[k]['value']=0
    c['prior'].update(value=-Q,disposition='USABLE')
    r=run_budget(b)
    assert len(r['rows'])==1 and r['rows'][0]['weight']==W and r['rows'][0]['z_fp']<0
    assert r['rows'][0]['allocation']==6 and r['unallocated']==1
    for disposition in ('TAMPERED','UNVERIFIED'):
        c['prior']['disposition']=disposition
        with pytest.raises(ValueError,match='unverified_prior'): run_budget(b)
    c['prior'].update(value=0,disposition='NONMATCHING')
    assert run_budget(b)['status']=='ALLOCATED'


def test_permutations_and_opaque_renaming():
    d=fixture()['strategy']; before=run_strategy(d)
    d['candidates'].reverse(); d['disagreements'].reverse(); d['context']['participants'].reverse()
    for c in d['candidates']: c['participants'].reverse(); c['required_roots'].reverse(); c['utilities'].reverse()
    assert run_strategy(d)==before
    b=fixture()['budget']; expected=run_budget(b); b['pressure_inputs']['branches'].reverse()
    assert run_budget(b)==expected
    for c in d['candidates']:
        c['id']=c['id'].replace('candidate:','alternative:')
        for u in c['utilities']: u['candidate_id']=c['id']
    renamed=run_strategy(d)
    assert renamed['recommendation'].endswith(':B')
    assert [x['product'] for x in renamed['scores']]==[x['product'] for x in before['scores']]


def test_decimal_ambient_isolation():
    expected=run_budget(fixture()['budget'])
    with localcontext() as ctx:
        ctx.prec=3; ctx.rounding=ROUND_DOWN; ctx.Emax=3; ctx.Emin=-3; ctx.clamp=1; ctx.capitals=0
        for signal in ctx.traps: ctx.traps[signal]=True
        before=str(ctx)
        assert run_budget(fixture()['budget'])==expected
        assert str(getcontext())==before
    assert _weights({})=={}


def test_penalty_boundaries_and_weak_ir():
    d=fixture()['strategy']
    d['candidates']=d['candidates'][:1]
    for u in d['candidates'][0]['utilities']:
        u['terms'][0]['feature_fp']=-Q
        u['penalties']=dict(risk=Q,latency=Q,coordination=Q)
    for item in d['disagreements']: item['value']=-4*Q
    r=run_strategy(d)
    assert all(u['utility']==-4*Q and u['gain']==0 for u in r['utilities'])
    assert r['status']=='NO_DEAL_ALL_ZERO_GAIN'
    d['candidates'][0]['utilities'][0]['terms'][0]['feature_fp']=-Q+1
    r=run_strategy(d)
    assert r['status']=='RECOMMENDATION' and r['weak_ir']


def test_saturation_cascade_and_equal_tie_order():
    ids=['g4_reference:b'+str(i) for i in range(3)]
    r=_apportion(12,dict(zip(ids,[0,0,0])),dict(zip(ids,[1,4,20])),dict(zip(ids,[100,10,1])))
    assert len(r['rounds'])==3 and [len(x['saturated']) for x in r['rounds']]==[1,1,0]
    assert list(r['allocations'].values())==[1,4,7]
    tie=_apportion(1,dict(zip(ids,[0,0,0])),dict(zip(ids,[3,3,3])),dict(zip(ids,[1,1,1])))
    assert tie['awards']==[ids[0]] and tie['order']==ids


def test_pressure_extremes_and_renamed_ids():
    b=fixture()['budget']; first,second=b['pressure_inputs']['branches']
    for k in ('relevance','lineage'): first[k]['value']=0; second[k]['value']=Q
    for k in ('uncertainty','cost'): first[k]['value']=Q; second[k]['value']=0
    first['prior'].update(value=-Q,disposition='USABLE'); second['prior'].update(value=Q,disposition='USABLE')
    r=run_budget(b)
    assert [row['z_fp'] for row in r['rows']]==[-500000000,875000000]
    expected=[row['allocation'] for row in r['rows']]
    for branch in b['pressure_inputs']['branches']: branch['id']=branch['id'].replace('branch:','renamed:')
    for m in b['mandatory']: m['branch_ref']=m['branch_ref'].replace('branch:','renamed:')
    assert [row['allocation'] for row in run_budget(b)['rows']]==expected


def large_unknown_strategy_v42(count):
    d=fixture()['strategy']; template=deepcopy(d['candidates'][0]); d['candidates']=[]
    context_count=max(0,count-512); remaining=count-context_count
    for i in range((remaining+15)//16):
        c=deepcopy(template); c['id']='g4_reference:unknown_candidate:'+str(i); c['utilities']=[]
        c['source_ref']='g4_reference:unknown_source:'+str(i)
        c['hard']=[dict(id='g4_reference:hard:'+str(j),state='UNKNOWN',evidence_ref=f'g4_reference:unknown:{i}:{j}') for j in range(min(16,remaining-i*16))]
        d['candidates'].append(c)
    if context_count:
        d['context']['dispositions']=[dict(id=f'g4_reference:context:{i}',state='UNKNOWN',source_ref=f'g4_reference:context_source:{i}') for i in range(context_count)]
    return seal_strategy(d)


def large_unknown_budget_v42(count):
    b=fixture()['budget']; template=deepcopy(b['pressure_inputs']['branches'][0]); branches=[]
    for i in range(16):
        v=deepcopy(template); v['id']=f'g4_reference:unknown_branch:{i}'; v['material_ref']=f'g4_reference:unknown_material:{i}'
        v['hard']=[dict(id=f'g4_reference:hard:{j}',state='UNKNOWN',evidence_ref=f'g4_reference:branch_unknown:{i}:{j}') for j in range(16)]
        v['available']='UNKNOWN' if i<min(16,count-256) else 'TRUE'; branches.append(v)
    b['pressure_inputs']['branches']=branches
    b['mandatory'][0].update(branch_ref=branches[0]['id'],material_ref=branches[0]['material_ref'])
    if count>272:
        b['context']['dispositions']=[dict(id=f'g4_reference:context:{i}',state='UNKNOWN',source_ref=f'g4_reference:context_source:{i}') for i in range(count-272)]
    return seal_budget(b)


@pytest.mark.parametrize('count',[256,257,272,544])
def test_strategy_missing_reference_capacity_v42(count):
    from hedgehog.gate4_strategy_reference_v01 import validate_reference_strategy_report_v01
    d=large_unknown_strategy_v42(count); assert len(ReferenceValueV01('strategy_input',d).canonical)<262144
    r=strategy(d,independently_bound_context=d['context'])
    assert r.plain()['status']=='NEEDS_MORE_EVIDENCE' and r.plain()['recommendation'] is None
    assert len(r.plain()['missing_refs'])==count
    bad=r.plain(); bad['missing_refs'].pop()
    with pytest.raises(ValueError,match='supplied_report_mismatch'):
        validate_reference_strategy_report_v01(ReferenceValueV01('strategy_report',bad),inputs=d,source_basis=d['context'])
    assert validate_reference_strategy_report_v01(r,inputs=d,source_basis=d['context'])==r
    assert run_strategy(fixture()['strategy'])['status']=='RECOMMENDATION'


@pytest.mark.parametrize('count',[256,257,272,304])
def test_pressure_allocation_missing_reference_capacity_v42(count):
    from hedgehog.gate4_pressure_budget_v01 import validate_reference_allocation_v01
    b=large_unknown_budget_v42(count); assert len(ReferenceValueV01('budget',b).canonical)<262144
    p=pressure(b['pressure_inputs'],profile=PROFILE); r=allocate(p,current_budget_context=b)
    assert len(p.plain()['missing_refs'])==len(r.plain()['missing_refs'])==count
    assert r.plain()['status']=='NEEDS_MORE_EVIDENCE' and not r.plain()['rows']
    bad=r.plain(); bad['missing_refs'].pop()
    with pytest.raises(ValueError,match='supplied_report_mismatch'):
        validate_reference_allocation_v01(ReferenceValueV01('allocation_report',bad),inputs=b['pressure_inputs'],current_budget_context=b)
    assert validate_reference_allocation_v01(r,inputs=b['pressure_inputs'],current_budget_context=b)==r
    assert run_budget(fixture()['budget'])['status']=='ALLOCATED'
