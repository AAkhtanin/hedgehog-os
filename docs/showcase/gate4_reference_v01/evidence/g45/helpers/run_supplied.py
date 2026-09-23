"""Invoke the one authorized installed-source supplied validation with receipts."""
from g45 import W,O,PY,read,run
state=read(W/'owner_finalize_state.json')
assert state['context']['state']=='FINALIZED'
run('installed_supplied',[PY,'-B',W/'supplied_installed.py'],cwd=O,env_extra={'PYTHONPATH':str(O)})
