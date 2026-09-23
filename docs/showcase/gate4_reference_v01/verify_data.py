#!/usr/bin/env python3
"""Data-only Gate 4 capsule checks. No project imports or code execution.

Uses only the standard library. Evidence/source files are parsed as data;
source/test locators are read with ast, never imported. No network or subprocess.
"""
from __future__ import annotations
import argparse,ast,hashlib,json,os,re,stat
from collections import Counter
from pathlib import Path,PurePosixPath
import xml.etree.ElementTree as ET

NAME='LLM_READER_GATE4_REFERENCE_V01'
DETACHED={NAME+'.xml','READER_INDEX.json',NAME+'.build.json','reader_content_manifest_v01.json','SHA256SUMS','MANIFEST.json','data_verification.json','qa/data_verification.json','qa/reader_qa.json'}
class NoDTDTreeBuilder(ET.TreeBuilder):
    def doctype(self,name,pubid,system):raise ValueError('XML DTD is forbidden')
EXPECTED_PUBLICATION='8e7c4cb6412981436b704d2cc94736de91783d93a77849076007725029d9d08f'
EXPECTED_PROOF='16cee34833de46c4fd03dee9da3990d03815237567dfecc7cc9870f69d6d6f02'
EXPECTED_PARENT='109c37f42ca220782971991c63f40037041d5c4548997fa1ab11262c578c81cd'
EXPECTED_COMBINED='136b2a76da196e42923886ffc5cf47d89e51d99ec8cc6c7ac549cfaea106b4b9'
def sha(b):return hashlib.sha256(b).hexdigest()
def require(value,reason):
    if not value:raise ValueError(reason)
def valid(s):
    p=PurePosixPath(s)
    require(bool(s) and not p.is_absolute() and '..' not in p.parts and '\\' not in s and p.as_posix()==s and not any(ord(c)<32 for c in s),'Unsafe path '+repr(s))
    return s
def get(root,s):
    valid(s);p=root/s
    for part in (p,*p.parents):
        if part==root.parent:break
        require(not part.is_symlink(),'Symlink '+s)
    require(p.is_file() and p.resolve().is_relative_to(root),'Missing/nonregular '+s)
    require(stat.S_ISREG(p.stat().st_mode),'Not regular '+s)
    return p.read_bytes()
def js(root,s):return json.loads(get(root,s))
def identity(root,path,row):
    b=get(root,path);require(len(b)==row['bytes'],'Size mismatch '+path);require(sha(b)==row['sha256'],'SHA mismatch '+path)
    if 'mode' in row:require(f'{stat.S_IMODE((root/path).stat().st_mode):04o}'==row['mode'],'Mode mismatch '+path)
    return b
def pointer(obj,p):
    if p.startswith('#'):p=p[1:]
    require(p=='' or p.startswith('/'),'Invalid JSON pointer '+p)
    if not p:return obj
    for raw in p[1:].split('/'):
        require(not re.search(r'~(?![01])',raw),'Invalid JSON pointer escape')
        key=raw.replace('~1','/').replace('~0','~')
        if isinstance(obj,list):
            require(bool(re.fullmatch(r'0|[1-9][0-9]*',key)),'Invalid array pointer index');obj=obj[int(key)]
        else:obj=obj[key]
    return obj

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--capsule',type=Path,default=Path(__file__).parent);ap.add_argument('--output',type=Path);args=ap.parse_args();root=args.capsule.resolve()
    manifest=js(root,'reader_content_manifest_v01.json');rows=manifest['members'];declared=set();casefold=set()
    for row in rows:
        path=valid(row['path']);require(path not in declared and path.casefold() not in casefold,'Duplicate/casefold path '+path);declared.add(path);casefold.add(path.casefold());identity(root,path,row)
    actual=set();all_casefold=set()
    for parent,dirs,names in os.walk(root,followlinks=False):
        for name in dirs+names:
            p=Path(parent)/name;m=p.lstat().st_mode;rel=p.relative_to(root).as_posix();valid(rel)
            require(stat.S_ISREG(m) or stat.S_ISDIR(m),'Nonregular member '+rel)
            require(rel.casefold() not in all_casefold,'Inventory casefold collision '+rel);all_casefold.add(rel.casefold())
            if stat.S_ISREG(m):actual.add(rel)
    excluded=set(manifest['detached_exclusions']);require(excluded==DETACHED and not (excluded & declared),'Unexpected detached exclusions or self-inclusion');require(actual-excluded==declared,'Inventory mismatch: missing '+repr(sorted(declared-actual))+' extra '+repr(sorted(actual-excluded-declared)))
    proof='evidence/g44/portable_publication_final/'
    require(sha(get(root,proof+'PUBLICATION.json'))==EXPECTED_PUBLICATION,'Original publication pin mismatch')
    require(sha(get(root,proof+'MANIFEST.json'))==EXPECTED_PROOF,'Original proof pin mismatch')
    p=js(root,proof+'MANIFEST.json');require(len(p['entries'])==222,'Proof row count')
    for row in p['entries']:identity(root,proof+row['path'],row)
    actual_proof={s[len(proof):] for s in declared if s.startswith(proof)}
    require(actual_proof=={r['path'] for r in p['entries']}|{'PUBLICATION.json','MANIFEST.json'},'Proof inventory mismatch')
    parent='evidence/g44/parents/';require(sha(get(root,parent+'MANIFEST.json'))==EXPECTED_PARENT,'Original parent pin mismatch')
    par=js(root,parent+'MANIFEST.json');require(len(par['files'])==75,'Parent row count')
    for path,row in par['files'].items():identity(root,parent+path,row)
    require({s[len(parent):] for s in declared if s.startswith(parent)}==set(par['files'])|{'MANIFEST.json'},'Parent inventory mismatch')
    trust=js(root,'evidence/g44/TEST_SUPPLIED_PIN_FINAL.json');require(trust['status']=='TEST_SUPPLIED_PIN' and trust['publication_sha256']==EXPECTED_PUBLICATION,'Changed test trust origin')
    require(get(root,'evidence/g44/PARENT_PIN.txt').decode().strip()==EXPECTED_PARENT,'Parent trust pin mismatch')
    sources=js(root,'source_snapshot/source_binding_index.json')
    for key,count in [('installed_postimages',34),('current_checker_closure',123),('recorded_producer_closure',34)]:
        require(len(sources[key])==count,key+' row count')
        for row in sources[key]:identity(root,row['path'],row)
    for row in sources['retained_parent_closure']:identity(root,row['path'],row)
    for key,ledger,folder in [('current_checker_closure',p['checker_source_ledger'],'checker_sources'),('recorded_producer_closure',p['producer_source_ledger'],'sources')]:
        actual_bindings={r['repository_path']:{'bytes':r['bytes'],'sha256':r['sha256']} for r in sources[key]}
        require(len(actual_bindings)==len(sources[key]) and actual_bindings==ledger,'Source closure ledger mismatch '+key)
        require(all(r['path']==proof+folder+'/'+r['repository_path'] for r in sources[key]),'Source closure path mismatch')
    retained={r['repository_path']:{'bytes':r['bytes'],'sha256':r['sha256']} for r in sources['retained_parent_closure']}
    expected_retained={k[len('sources/'):]:v for k,v in par['files'].items() if k.startswith('sources/')}
    require(len(retained)==len(sources['retained_parent_closure']) and retained==expected_retained,'Retained source closure mismatch')
    require(all(r['path']==parent+'sources/'+r['repository_path'] for r in sources['retained_parent_closure']),'Retained source path mismatch')
    installed_paths={r['path'] for r in sources['installed_postimages']}
    require(len(installed_paths)==34 and installed_paths=={r['path'] for r in js(root,'evidence/original_member_index.json')['members'] if r['original'].startswith('g45/postimages/')},'Installed postimage coverage mismatch')
    for row in js(root,'evidence/original_member_index.json')['members']:identity(root,row['path'],row)
    combined=[get(root,x) for x in ['evidence/g44/commands/0020_supplied_living_final/combined.json','evidence/g44/commands/0021_supplied_conformance_final/combined.json','evidence/g45/installed_supplied/combined.json']]
    require(combined[0]==combined[1]==combined[2],'Full combined byte mismatch');require(len(combined[0])==1151634 and sha(combined[0])==EXPECTED_COMBINED,'Combined canonical pin')
    run=js(root,'evidence/g45/installed_supplied/execution.json');require(run['rc']==0 and all(v==0 for v in run['forbidden_calls'].values()) and all(v==0 for v in run['audit'].values()),'Saved instrumented counters')
    idx=js(root,'READER_INDEX.json');raw=get(root,NAME+'.xml');require(len(raw)==idx['reader_bytes'] and sha(raw)==idx['reader_sha256'],'Reader digest mismatch');require(sha(get(root,'reader_content_manifest_v01.json'))==idx['content_manifest_sha256'],'Detached manifest mismatch')
    tree=ET.fromstring(raw,parser=ET.XMLParser(target=NoDTDTreeBuilder()));require(tree.tag=='repomix' and [c.tag for c in tree]==['file_summary','files'],'Unexpected XML structure');nodes=list(tree.find('files'));require(all(n.tag in ('file','binary_member') for n in nodes),'Unexpected XML member tag');require(len(nodes)==len(rows),'XML count mismatch');seen=set();by_path={r['path']:r for r in rows}
    for node in nodes:
        path=node.attrib['path'];require(path not in seen and path in by_path,'Unexpected/duplicate XML path');seen.add(path);row=by_path[path]
        for key in ('id','path','kind','sha256','encoding','mode'):require(node.attrib[key]==str(row[key]),'XML attribute mismatch '+path)
        require(int(node.attrib['bytes'])==row['bytes'],'XML length attribute')
        require(len(node)==0,'Unexpected XML member children')
        if node.tag=='file':require(row['encoding']=='utf-8' and (node.text or '').encode('utf-8')==get(root,path),'XML body/classification mismatch '+path)
        else:require(row['encoding']=='binary-external' and not node.text,'Unexpected binary classification/body')
    require({r['path'] for r in idx['members']}==declared and len(idx['members'])==len(rows),'Index member mismatch')
    require(idx['member_count']==len(rows) and idx['reader']==NAME+'.xml' and idx['content_manifest']=='reader_content_manifest_v01.json','Index target/count mismatch')
    line_offsets=[0]
    for n,b in enumerate(raw):
        if b==10:line_offsets.append(n+1)
    import bisect
    for ordinal,r in enumerate(idx['members'],1):
        require(all(r[k]==by_path[r['path']][k] for k in by_path[r['path']]),'Index row mismatch')
        pos=r['reader_position'];start=pos['byte_start'];end=pos['byte_end_exclusive']
        require(type(start) is int and type(end) is int and 0<=start<end<=len(raw),'Unsafe index offset')
        require(pos['ordinal']==ordinal and pos['line_start']==bisect.bisect_right(line_offsets,start) and pos['line_end']==bisect.bisect_right(line_offsets,end),'Index line/ordinal mismatch')
        fragment=raw[start:end]
        require(fragment.startswith(b'<file ') or fragment.startswith(b'<binary_member '),'Index offset mismatch')
        fragment_node=ET.fromstring(fragment);node=next(n for n in nodes if n.attrib['path']==r['path']);require(fragment_node.tag==node.tag and fragment_node.attrib==node.attrib and fragment_node.text==node.text and len(fragment_node)==0,'Index position target mismatch')
    slides=js(root,'presentation/slide_text_and_notes_v01.json')['slides'];require(len(slides)==12 and {s['number'] for s in slides}==set(range(1,13)),'Expected 12 numbered presentation slides')
    appendix_anchors=js(root,'presentation/appendix_anchors.json')
    appendix_text=get(root,'technical_appendix_v01.md').decode('utf-8')
    routepath='presentation/claim_evidence_matrix_v01.json';claims=js(root,routepath)['claims'];claim_ids=set();locator_count=0;ast_cache={};json_cache={}
    for claim in claims:
        cid=claim['claim_id'];require(cid not in claim_ids,'Duplicate claim '+cid);claim_ids.add(cid);require(claim['source_refs'] and claim['data_refs'],'Empty claim route '+cid);require(claim['anchors']['reader']==cid,'Wrong Reader claim anchor')
        require(isinstance(claim['anchors']['slides'],list) and all(type(x) is int and 1<=x<=len(slides) for x in claim['anchors']['slides']),'Invalid slide anchors '+cid)
        anchor=claim['anchors']['appendix'];require(anchor in appendix_anchors,'Missing actual appendix anchor '+cid)
        require('id="'+anchor+'"' in appendix_text,'Missing Markdown anchor '+cid)
        target=appendix_anchors[anchor];require(type(target['page']) is int and target['page']>0 and target['title'] in appendix_text,'Missing actual appendix page/title '+cid)
        require(all(cid in slides[n-1]['claim_ids'] for n in claim['anchors']['slides']),'Claim/slide map disagreement '+cid)
        for key in ('source_refs','test_refs','data_refs','positive_refs','negative_refs','consumer_refs'):
            for ref in claim.get(key,[]):
                path=ref['path'];require(path in declared,'Undeclared claim path '+path);body=get(root,path)
                if 'sha256' in ref:require(sha(body)==ref['sha256'],'Claim reference SHA '+cid+' '+path)
                if ref.get('json_pointer') is not None:
                    if path not in json_cache:json_cache[path]=json.loads(body)
                    pointer(json_cache[path],ref['json_pointer'])
                if ref.get('symbol'):
                    if path not in ast_cache:
                        parsed=ast.parse(body.decode('utf-8'),filename=path);names=set()
                        def definitions(node,prefix=''):
                            for child in ast.iter_child_nodes(node):
                                if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                                    qualified=prefix+child.name;names.add(qualified);definitions(child,qualified+'.')
                                else:definitions(child,prefix)
                        definitions(parsed);ast_cache[path]=names
                    require(ref['symbol'] in ast_cache[path],'Missing source/test symbol '+cid+' '+ref['symbol'])
                locator_count+=1
    require(claim_ids=={f'C{i:02d}' for i in range(1,17)},'Expected evidence routes C01-C16')
    result=dict(profile='GATE4_DATA_ONLY_VERIFICATION_V01',status='PASS',members=len(rows),reader_bytes=len(raw),reader_sha256=sha(raw),proof_manifest_rows=222,parent_manifest_rows=75,installed_postimages=34,current_checker_sources=123,historical_producer_sources=34,claim_routes=len(claim_ids),claim_locators_checked=locator_count,project_imports=0,project_code_executed=False,new_semantic_replay=False,checks=['safe regular inventory','file sizes modes and SHA256','proof and parent manifests and original pins','distinct source closures','three complete combined outputs byte-identical','saved named counters','XML bodies and detached index offsets','claim paths pointers symbols and anchors'])
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
