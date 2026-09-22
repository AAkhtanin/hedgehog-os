"""Direct supplied mechanism entrypoints, without autouse legacy E5 fixtures."""
import copy
import sys
import pytest
from tests.test_gate3_adversary_v01 import g36_bundle
from hedgehog import gate3_mechanism_v01 as mechanism


def test_g36_both_mechanism_consumers_and_zero_collection(g36_bundle):
    from demo import run_living_gauntlet_v01 as living,run_kernel_conformance_v01 as conformance
    from demo import run_continuous_delta_runtime_g2_e_v01 as e5
    from hedgehog.kernel import fractal_runtime_v02 as d,continuous_delta_runtime_v01 as e
    targets={fn.__code__:0 for fn in (e5.collect_continuous_delta_runtime_g2_e_v01,mechanism.collect_mechanism_v01,d.run_fractal_runtime_v02,e.run_continuous_delta_runtime_v01)}
    tool=4;sys.monitoring.use_tool_id(tool,'g36_consumer_observer')
    def hit(code,offset):targets[code]+=1
    sys.monitoring.register_callback(tool,sys.monitoring.events.PY_START,hit)
    for code in targets:sys.monitoring.set_local_events(tool,code,sys.monitoring.events.PY_START)
    try:
        a=living.consume_gate3_mechanism_v01(g36_bundle);b=conformance.consume_gate3_mechanism_v01(g36_bundle)
        assert a['mechanism']['report_id']==b['mechanism']['report_id']==g36_bundle['report']['report_id']
        assert a['checked_count']==b['checked_count']==len(mechanism.INVENTORY)
        assert all(v==0 for v in targets.values())
    finally:
        for code in targets:sys.monitoring.set_local_events(tool,code,0)
        sys.monitoring.free_tool_id(tool)


@pytest.mark.parametrize('consumer',['living','conformance'])
@pytest.mark.parametrize('change',['report','source','link'])
def test_g36_wrapper_rejects_coherent_bad_supplied_proof(g36_bundle,consumer,change):
    from demo import run_living_gauntlet_v01 as living,run_kernel_conformance_v01 as conformance
    value=copy.deepcopy(g36_bundle)
    if change=='report':value['report']['current']['consumed_work']='fabricated'
    elif change=='source':value['sources']['observations'][0]['request']['independent_policy']['maximum_minor']=1700
    else:value['sources']['current']['work']['proposal']['payload']['bridge_ref']='foreign'
    value['report']['report_id']=mechanism.digest({k:v for k,v in value['report'].items() if k!='report_id'})
    value['baseline']=mechanism.independent_baseline_v01(value['sources'])
    with pytest.raises(ValueError):
        (living if consumer=='living' else conformance).consume_gate3_mechanism_v01(value)


def test_g36_successor_cannot_replace_full_legacy_report_with_g3_pass(g36_bundle):
    from demo import run_living_gauntlet_v01 as living,run_kernel_conformance_v01 as conformance
    for profile,consume,validate in (
        ('LIVING_G36_SUCCESSOR_V01',living.consume_gate3_mechanism_v01,living.validate_living_g36_v01),
        ('KERNEL_CONFORMANCE_G36_SUCCESSOR_V01',conformance.consume_gate3_mechanism_v01,conformance.validate_kernel_conformance_g36_v01)):
        value=dict(profile=profile,legacy={},gate3=consume(g36_bundle),gate3_bundle=g36_bundle,g3_collector_calls=1,e5_collector_calls=1)
        assert validate(value)
