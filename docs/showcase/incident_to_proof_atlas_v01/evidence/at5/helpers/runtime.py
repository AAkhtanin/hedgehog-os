"""One connected AT5 collector with an external final completion marker."""
import os
import sys
import time
from ops import *
sys.path.insert(0,str(CANDIDATE))
from hedgehog.domains.landslide_sentinel.incident_atlas_v01 import collect_sentinel_v01
label=sys.argv[1]
start=time.monotonic()
try:
    result=collect_sentinel_v01(WORK/label)
    print('SENTINEL_COMPLETE',result['seconds'],result['phases'],flush=True)
finally:
    save(WORK/(label+'_process_final.json'),dict(pid=os.getpid(),time=now(),seconds=time.monotonic()-start))
