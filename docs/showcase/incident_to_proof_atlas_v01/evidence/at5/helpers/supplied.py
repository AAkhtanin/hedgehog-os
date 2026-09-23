"""Validate a preserved actual return, adding only its immutable episode trace."""
import sys
from ops import *
sys.path.insert(0,str(CANDIDATE))
from hedgehog.domains.landslide_sentinel.incident_atlas_proof_v01 import validate_sentinel_v01
directory=WORK/'0005_sentinel'
value=json.loads((directory/'sentinel.json').read_bytes())
value['episode_trace']=[json.loads(v) for v in (directory/'continuing_episode/phases.jsonl').read_text().splitlines()]
save(WORK/'sentinel_supplied.json',value)
result=validate_sentinel_v01(value)
save(WORK/'supplied_result.json',result)
print(result)
