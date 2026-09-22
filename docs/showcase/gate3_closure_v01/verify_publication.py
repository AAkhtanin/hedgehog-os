#!/usr/bin/env python3
"""Verify publication integrity only; never import or execute archived source."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, stat
p=argparse.ArgumentParser();p.add_argument('--expected-manifest-sha256',required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;m=root/'MANIFEST.json';b=m.read_bytes()
if hashlib.sha256(b).hexdigest()!=a.expected_manifest_sha256:raise SystemExit('FAIL: external manifest pin mismatch')
rows=json.loads(b)['files'];seen=set()
for r in rows:
    s=r['path'];q=PurePosixPath(s)
    if q.is_absolute() or '..' in q.parts or s in seen:raise SystemExit('FAIL: unsafe or duplicate path')
    seen.add(s);f=root/s
    if f.is_symlink() or not f.is_file():raise SystemExit('FAIL: missing or nonregular file: '+s)
    data=f.read_bytes()
    if len(data)!=r['bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256']:raise SystemExit('FAIL: byte identity: '+s)
    if stat.S_IMODE(f.stat().st_mode)!=int(r['mode'],8):raise SystemExit('FAIL: mode: '+s)
actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file() or f.is_symlink()}
if actual!=seen|{'MANIFEST.json'}:raise SystemExit('FAIL: manifest coverage')
print(json.dumps({'status':'PASS','scope':'PUBLICATION_BYTE_INTEGRITY_ONLY','files':len(rows),'manifest_sha256':a.expected_manifest_sha256}))
