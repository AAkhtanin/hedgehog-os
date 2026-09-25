"""Explicit offline Gate5 proof command; never starts peers or candidate code."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/gate5_reference_evidence_v01'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()

def relative(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == name, 'unsafe path')
    return p

def regular(path):
    require(path.is_file() and not path.is_symlink(), 'regular file required: ' + str(path))
    require(not any(p.is_symlink() for p in path.parents), 'symlink parent')
    return path.read_bytes()

def materialize(out, index):
    blobs = {}
    with tarfile.open(EVIDENCE / 'material.tar.gz', 'r:gz') as archive:
        total = 0
        for item in archive:
            name = relative(item.name)
            require(item.isfile() and len(name.parts) == 2 and name.parts[0] == 'blobs', 'non-blob member')
            total += item.size
            require(total <= 600_000_000 and item.size <= 40_000_000 and len(blobs) < 20000, 'material budget')
            require(item.name not in blobs, 'duplicate blob')
            data = archive.extractfile(item).read()
            require(digest(data) == name.name, 'blob hash')
            blobs[item.name] = data
    for label in ('g54d1', 'g52'):
        for name, row in index['members'][label].items():
            relative(name)
            storage = row['storage']
            data = (regular(ROOT / relative(storage['repository'])) if 'repository' in storage
                    else blobs['blobs/' + storage['blob']])
            require(len(data) == row['bytes'] and digest(data) == row['sha256'], 'member binding: ' + name)
            p = out / label / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
    return blobs

def author_reconstruction(d1):
    """Replay the accepted broker's inert text operations, never its code."""
    trial = d1/'AUTHOR_TRIAL'
    seed = read(trial/'seeded_source.json')['files']
    before = d1/'PREDECESSOR/AUTHOR_TRIAL/attempt_03/candidate'
    data = {}
    for row in seed:
        b = regular(before/relative(row['path']))
        require(len(b) == row['bytes'] and digest(b) == row['sha256'], 'author seed')
        data[row['path']] = b
    calls = read(trial/'session/tool_results.json')
    submitted = 0
    identities = set()
    for row in calls:
        request, response = row['request'], row['response']
        identity = tuple(request[k] for k in ('threadId','turnId','callId'))
        require(identity not in identities, 'duplicate broker call')
        identities.add(identity)
        if response.get('status') == 'TOOL_REFUSED':
            continue
        name, args = request['tool'], request['arguments']
        if name in ('write_candidate_file','patch_candidate_file'):
            require(not submitted, 'post-submission author edit')
            path = str(relative(args['path']))
            if name == 'write_candidate_file':
                data[path] = args['content'].encode()
            else:
                require(digest(data[path]) == args['expected_sha256'], 'patch predecessor')
                text = data[path].decode()
                require(text.count(args['old']) == 1, 'patch occurrence')
                data[path] = text.replace(args['old'],args['new'],1).encode()
            require(digest(data[path]) == response['sha256'] and len(data[path]) == response['bytes'], 'broker response')
        elif name == 'submit_candidate':
            require(not submitted, 'multiple submissions')
            submitted += 1
            manifest = dict(version='g53.candidate.v01', candidate_id=args['candidate_id'], entrypoint='candidate_domain.run',installable_now=False,
                            files=[dict(path=p,bytes=len(b),sha256=digest(b)) for p,b in sorted(data.items())])
            data['candidate.json'] = (json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    actual = {str(p.relative_to(trial/'attempt_04/candidate')):regular(p) for p in (trial/'attempt_04/candidate').rglob('*') if p.is_file()}
    require(data == actual and len(actual) == 24 and submitted == 1 and len(calls) == 79, 'author reconstruction')
    return dict(seed_files=len(seed),broker_operations=len(calls),submissions=1,final_files=len(actual),correction_index=4,total_submissions=5)

def run(argv, cwd, env, out, label):
    start = time.monotonic()
    with (out / (label + '.stdout')).open('wb') as stdout, (out / (label + '.stderr')).open('wb') as stderr:
        p = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr)
        rc = p.wait()
    receipt = dict(argv=argv, cwd=str(cwd), pid=p.pid, rc=rc, reaped=True,
                   elapsed_seconds=time.monotonic()-start,
                   streams={n:dict(bytes=(out/(label+'.'+n)).stat().st_size,
                                   sha256=digest((out/(label+'.'+n)).read_bytes())) for n in ('stdout','stderr')})
    (out / (label + '.receipt.json')).write_bytes(canonical(receipt))
    require(rc == 0, label + ' refused; see raw stderr')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory outside repository')
    args = parser.parse_args()
    out = args.output.absolute()
    require(not out.resolve().is_relative_to(ROOT), 'proof output must be external')
    out.mkdir(parents=True, exist_ok=False)
    freeze = read(EVIDENCE / 'proof_input_freeze.json')
    for name, pin in freeze['files'].items():
        b = regular(ROOT / relative(name))
        require(digest(b) == pin['sha256'] and len(b) == pin['bytes'], 'input freeze: ' + name)
    bindings = read(EVIDENCE / 'source_bindings.json')
    for name, row in bindings['paths'].items():
        require(digest(regular(ROOT / relative(name))) == row['sha256'], 'installed source: ' + name)
    for row in bindings['dependency_comparisons']:
        if row['comparison'] == 'BYTE_IDENTICAL':
            require(digest(regular(ROOT / relative(row['destination']))) == row['sha256'], 'dependency: ' + row['destination'])
    index = read(EVIDENCE / 'member_index.json')
    materialize(out, index)
    d1 = out / 'g54d1'
    author = author_reconstruction(d1)
    historical = out / 'g52_source'
    shutil.copytree(d1 / 'AUTHOR_VISIBLE/source', historical)
    g52 = out / 'g52'
    for p in (g52 / 'postimages').rglob('*'):
        if p.is_file():
            dest = historical / p.relative_to(g52/'postimages')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
    expected = read(g52/'evidence/expected_capture.json')
    for name, pin in expected['source_pins'].items():
        p = historical / relative(name)
        if not p.exists():
            b = regular(ROOT / relative(name))
            require(digest(b) == pin, 'historical missing source')
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b)
        require(digest(p.read_bytes()) == pin, 'G52 historical source identity')
    env = {k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONSTARTUP','HEDGEHOG_REPOSITORY_REVIEW_CONTEXT_V01')}
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(historical))
    run([sys.executable,'-B',str(g52/'helpers/run_supplied.py'),str(g52/'evidence/lifecycle_06'),
         str(g52/'evidence/expected_capture.json'),str(historical),str(out/'g52_result.json')],g52,env,out,'g52')
    env['PYTHONPATH'] = str(d1/'AUTHOR_VISIBLE/source')
    run([sys.executable,'-B',str(d1/'supplied_check_d1.py'),str(out/'d1_result.json')],d1,env,out,'d1')
    require((out/'d1_result.json').read_bytes() == (d1/'SUPPLIED/one.json').read_bytes(), 'D1 recorded parity')
    require((d1/'SUPPLIED/one.json').read_bytes() == (d1/'SUPPLIED/two.json').read_bytes(), 'D1 recorded dual parity')
    require((out/'g52_result.json').read_bytes() == (g52/'evidence/proofs/supplied_03.json').read_bytes(), 'G52 recorded parity')
    result = dict(status='PASS_PURE_SOURCE_BOUND_CLOSURE', input_freeze_sha256=digest((EVIDENCE/'proof_input_freeze.json').read_bytes()),
        g52=read(out/'g52_result.json'),d1=read(out/'d1_result.json'),author_reconstruction=author,
        installed_sources_checked=len(bindings['paths']),dependency_comparisons=len(bindings['dependency_comparisons']),
        orchestration_pure_subprocesses=2,author_calls=0,provider_calls=0,candidate_imported=False,
        classification='HISTORICAL_G52_AND_ACCEPTED_D1_SUPPLIED_VERIFICATION_NOT_FRESH_NATIVE')
    (out/'canonical_result.json').write_bytes(canonical(result))
    print(json.dumps(dict(status=result['status'],sha256=digest(canonical(result)),bytes=len(canonical(result)),pure_subprocesses=2)))

if __name__ == '__main__':
    main()
