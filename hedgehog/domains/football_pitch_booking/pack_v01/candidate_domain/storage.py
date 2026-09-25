"""Own-directory data only. No path is accepted from a peer payload."""
import json
import re
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_exchange_v01 as x
from candidate_domain.domain import need

def local_name(value):
    need(type(value) is str and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}',value) is not None,
         'event_id_unsafe')
    return value

def read(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text())

def save(path,value):
    x.immutable(path,value)

def state(path,value):
    x.state_write(path,value)

def identity(r):
    return c.sha({k:r[k] for k in ('request_id','team_ref','venue_ref','revision')})

def history_path(root,r):
    return root/'offers'/(identity(r)+'.json')

def object_path(root,r):
    return root/'bookings'/(c.sha({k:r[k] for k in ('request_id','team_ref','venue_ref')})+'.json')
