"""Focused saved-evidence checks; no implicit producer or model calls."""
import os,sys,json
from ops import WORK,CANDIDATE,save
sys.path.insert(0,str(CANDIDATE))
os.environ['AT1_SAVED_SUPPLIER']=str(WORK/'retained/supplier.json')
os.environ['AT1_SAVED_EXPORT']=str(WORK/'export')
os.environ['AT2_SAVED_AIRLINE']=str(WORK/'retained/airline.json')
os.environ['AT3_SAVED_TESTFLIX']=str(WORK/'retained/testflix.json')
os.environ['AT4_SAVED_WORKSPACE']=str(WORK/'retained/workspace.json')
os.environ['AT5_SAVED_SENTINEL']=str(WORK/'sentinel_supplied.json')
import pytest
label=sys.argv[1]
class Phases:
    def pytest_runtest_logreport(self,report):
        with (WORK/(label+'_phases.jsonl')).open('a') as stream:
            stream.write(json.dumps(dict(node=report.nodeid,phase=report.when,outcome=report.outcome,seconds=report.duration,
                error=str(report.longrepr) if report.failed else None))+'\n')
    def pytest_sessionfinish(self,session,exitstatus):
        save(WORK/(label+'_finalizer.json'),dict(rc=int(exitstatus),nodes=session.testscollected,failed=session.testsfailed))
nodes=sys.argv[2:] or ['tests/test_incident_atlas_v01.py','tests/test_incident_atlas_supplier_v01.py',
    'tests/test_incident_atlas_airline_v01.py','tests/test_incident_atlas_testflix_v01.py',
    'tests/test_incident_atlas_workspace_v01.py','-k','not native_channel_smoke']
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider',*nodes],plugins=[Phases()]))
