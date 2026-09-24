"""Deterministic report bytes and a separate current, write-once local boundary."""
from html import escape
import os
from pathlib import Path
import time
from . import native_contracts_v01 as c, native_adapter_v01 as native, runtime_v01 as runtime
from .qpu_bridge_v01 import atomic_json

def render_v01(output,problem):
    c.require(output['origin']=='LIVE_QPU_RAW_DECODED_POSTSELECTED','render_raw_origin')
    tables=[]
    for i in range(3):
        guests=[g for g,t in zip(problem['guest_ids'],output['assignment']) if t==i]
        tables.append('<section><h2>Table '+str(i+1)+'</h2><svg viewBox="0 0 180 90" aria-label="Four seats at a table"><rect x="45" y="15" width="90" height="60" rx="6" fill="#e1e8e4"/>'+''.join('<circle cx="'+str(x)+'" cy="'+str(y)+'" r="10" fill="#287e60"/>' for x,y in ((28,28),(28,62),(152,28),(152,62)))+'</svg><ul>'+''.join('<li>'+escape(g)+'</li>' for g in guests)+'</ul></section>')
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wedding QPU Seating</title>'
        '<style>body{font:16px system-ui;color:#202923;margin:24px;max-width:1000px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:24px}section{border-top:3px solid #287e60}svg{max-width:200px}code{overflow-wrap:anywhere}li{margin:8px 0}</style>'
        '<h1>Wedding seating</h1><p>Synthetic 12-guest fixture. Rigetti raw measurements, classical postselection; no sample repair.</p><p>Objective: '+escape(output['profile'])+
        '. Gap to the recorded local optimum: '+str(output['objective_gap'])+'.</p><main>'+''.join(tables)+'</main><p>Task: <code>'+escape(output['task_arn'])+
        '</code></p><p>Raw SHA256: <code>'+output['raw_sha256']+'</code>; shot '+str(output['shot_index'])+', basis '+str(output['basis_index'])+'.</p><p>No quantum speedup, optimality or production-safety claim.</p></html>').encode()

def save_check_v01(claim,path,raw,now,*,revoked=False):
    c.require(not revoked and now<claim['expires'],'current_save_permission')
    c.require(str(path)==claim['path'] and c.digest(raw)==claim['sha256'] and len(raw)==claim['bytes'],'exact_save_bytes_path')
    c.require(not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'save_symlink')

def write_once_v01(claim,path,raw,now):
    path=Path(path);save_check_v01(claim,path,raw,now)
    if path.exists():
        c.require(path.read_bytes()==raw,'existing_save_differs');return 'ALREADY_SAVED_IDENTICAL'
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    c.require(path.read_bytes()==raw,'save_readback');return 'SAVED_READBACK_VERIFIED'

def save_current_v01(run,directory):
    c.require(type(run) is runtime.NativeRunV01 and run.owner.task_kind=='QPU_CONSUME','live_result_consumption')
    run.validate_current(run.owner)
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    reports=[]
    for name,raw in (('seating.json',c.canonical(run.output)),('seating.html',render_v01(run.output,run.material['problem']))):
        now=int(time.time());path=directory/name
        claim=dict(path=str(path),sha256=c.digest(raw),bytes=len(raw),expires=now+600,owner_scope='W4_NEW_TASK_OWNED_OUTPUT_ONLY')
        save_check_v01(claim,path,raw,now)
        root=native.root_review(run.material['problem']['owner_root_id'],'transaction:'+run.owner.request_ref,
            c.identity('wedding_save',claim),run.owner.request_ref,dict(actual_native_result=True,exact_output_bytes=True,local_owner_save_scope=True),
            run.evidence['artifact']['artifact_id'],run.program.candidate.bsep_ref,run.program.topology_artifact.artifact_id,now,
            predicate='wedding_current_local_save',permission='owner:W4:task_owned_local_output',claim_value=claim)
        c.require(not native.roots.validate_root_decision_result_v01(kernel=root[0],decision_input=root[1],result=root[2]),'save_root')
        status=write_once_v01(claim,path,raw,int(time.time()))
        row=dict(claim=claim,status=status,root_kernel=runtime.plain(root[0]),root_input=runtime.plain(root[1]),root_result=runtime.plain(root[2]))
        reports.append(row)
    atomic_json(directory/'save_receipts.json',reports)
    return reports
