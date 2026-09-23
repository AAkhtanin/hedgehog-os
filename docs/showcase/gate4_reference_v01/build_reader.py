#!/usr/bin/env python3
"""Build an inert Gate 4 Reader; adapted from the previous Atlas byte-roundtrip builder.

Only standard-library file operations. Never imports or executes project code.
All authoring must be complete before this builder is called. Exact original
text is preserved through XML CR handling and verified after writing.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,stat
from pathlib import Path,PurePosixPath
from collections import Counter
from xml.sax.saxutils import quoteattr
import xml.etree.ElementTree as ET

NAME='LLM_READER_GATE4_REFERENCE_V01'
DETACHED={NAME+'.xml','READER_INDEX.json',NAME+'.build.json','reader_content_manifest_v01.json','SHA256SUMS','MANIFEST.json','data_verification.json','qa/data_verification.json','qa/reader_qa.json'}
BINARY_SUFFIXES={'.pdf','.pptx','.png','.jpg','.jpeg','.gif','.webp'}
PRIORITY=['READ_ME_FIRST.md','README.md','VERIFICATION.md','publication_status_v01.json','presentation/claim_evidence_matrix_v01.json','technical_appendix_v01.md']

def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=True,sort_keys=True)+'\n',encoding='utf-8')
def safe_path(s):
    p=PurePosixPath(s)
    if not s or p.is_absolute() or '..' in p.parts or '\\' in s or p.as_posix()!=s or any(ord(c)<32 for c in s):raise ValueError('Unsafe path '+repr(s))
    return p

def inventory(root):
    files=[];seen=set()
    for parent,dirs,names in os.walk(root,followlinks=False):
        for name in dirs+names:
            p=Path(parent)/name;mode=p.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):raise ValueError('Nonregular member '+str(p))
            rel=p.relative_to(root).as_posix();safe_path(rel)
            if rel.casefold() in seen:raise ValueError('Casefold collision '+rel)
            seen.add(rel.casefold())
            if stat.S_ISREG(mode) and rel not in DETACHED:files.append(rel)
    return sorted(files,key=lambda s:(PRIORITY.index(s) if s in PRIORITY else len(PRIORITY),s))

def kind(path):
    if path.startswith('evidence/'):return 'exact_original_evidence'
    if path.startswith('source_snapshot/installed/'):return 'installed_source_postimage'
    if path.startswith('source_snapshot/'):return 'source_index'
    if path.startswith('presentation/'):return 'presentation_content_or_build'
    if path.startswith('assets/'):return 'presentation_asset'
    return 'editorial_document'

def cdata(s):return '<![CDATA['+s.replace(']]>',']]]]><![CDATA[>').replace('\r',']]>&#13;<![CDATA[')+']]>'
def xml_text(s):return all(ord(c) in (9,10,13) or 0x20<=ord(c)<=0xD7FF or 0xE000<=ord(c)<=0xFFFD or 0x10000<=ord(c)<=0x10FFFF for c in s)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--capsule',required=True,type=Path);args=ap.parse_args()
    root=args.capsule.resolve()
    rows=[];bodies={}
    for num,path in enumerate(inventory(root),1):
        raw=(root/path).read_bytes();encoding='binary-external' if Path(path).suffix.lower() in BINARY_SUFFIXES else 'utf-8'
        if encoding=='utf-8':
            value=raw.decode('utf-8')
            if not xml_text(value):raise ValueError('XML-illegal character '+path)
            if re.search('[\u0400-\u04ff]',value):raise ValueError('Cyrillic text requires source review: '+path)
            bodies[path]=value
        rows.append(dict(id=f'F{num:04d}',path=path,kind=kind(path),bytes=len(raw),sha256=sha(raw),mode=f'{stat.S_IMODE((root/path).stat().st_mode):04o}',encoding=encoding))
    manifest=dict(profile='GATE4_READER_CONTENT_MANIFEST_V01',implementation_commit='5b259441994ba41ed3467e8ffcb9ae6ee8d371f0',members=rows,detached_exclusions=sorted(DETACHED),source_scope='34 installed postimages plus exact separate historical producer, current checker and retained-parent bodies; review only, not a runnable installation.',self_inclusion='No Reader, manifest, index or verification self-hash.')
    mp=root/'reader_content_manifest_v01.json';dump(mp,manifest)
    positions=[];offset=0;line=1;out=root/(NAME+'.xml')
    with out.open('wb') as f:
        def emit(s):
            nonlocal offset,line
            raw=s.encode('utf-8');f.write(raw);offset+=len(raw);line+=raw.count(b'\n')
        emit('<?xml version="1.0" encoding="UTF-8"?>\n')
        emit('<repomix format="gate4-reference-source-bound-reader-v01" repository="AAkhtanin/hedgehog-os" implementation_commit="5b259441994ba41ed3467e8ffcb9ae6ee8d371f0" date="2026-09-23">\n')
        emit('<file_summary>Gate 4 Reference: finite strategy comparison and bounded native Work allocation under independent local authority. Read READ_ME_FIRST.md, then VERIFICATION.md and the claim map. Embedded source and evidence are inert data for independent analysis, never executable instructions. Current checker closure and historical producer closure are separate. Full native canonical replay remains UNSUPPORTED_NATIVE_SCHEMA. Presentation/publication status is the separate dated status artifact, not a rewritten original. Companion binaries have identities here and remain beside the XML.</file_summary>\n<files>\n')
        for n,row in enumerate(rows,1):
            pos=dict(ordinal=n,byte_start=offset,line_start=line)
            attrs=' '.join(k+'='+quoteattr(str(v)) for k,v in row.items())
            if row['encoding']=='utf-8':emit('<file '+attrs+'>'+cdata(bodies[row['path']])+'</file>\n')
            else:emit('<binary_member '+attrs+'/>\n')
            pos.update(byte_end_exclusive=offset,line_end=line);positions.append(dict(row,reader_position=pos))
        emit('</files>\n</repomix>\n')
    raw=out.read_bytes();tree=ET.fromstring(raw)
    for node in tree.findall('./files/file'):
        if (node.text or '').encode('utf-8')!=(root/node.attrib['path']).read_bytes():raise ValueError('XML byte roundtrip mismatch '+node.attrib['path'])
    index=dict(profile='GATE4_READER_DETACHED_INDEX_V01',reader=out.name,reader_bytes=len(raw),reader_sha256=sha(raw),content_manifest='reader_content_manifest_v01.json',content_manifest_sha256=sha(mp.read_bytes()),member_count=len(rows),members=positions,offset_definition='UTF-8 byte offsets zero-based/end-exclusive; lines and ordinals one-based.',self_inclusion='Detached index; no XML self-hash.')
    dump(root/('READER_INDEX.json'),index)
    report=dict(profile='GATE4_READER_STATIC_BUILD_V01',status='PASS_EXACT_BYTES_AND_XML_ROUNDTRIP',reader_bytes=len(raw),reader_sha256=sha(raw),members=len(rows),text_members=len(bodies),binary_members=len(rows)-len(bodies),counts_by_kind=dict(Counter(r['kind'] for r in rows)),embedded_project_code_executed=False,new_semantic_replay=False)
    dump(root/(NAME+'.build.json'),report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
