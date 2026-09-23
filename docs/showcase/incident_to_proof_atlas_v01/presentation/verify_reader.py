#!/usr/bin/env python3
"""Verify reader bytes, detached index and optional companion capsule; never execute contents."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('reader',type=Path);p.add_argument('--index',required=True,type=Path)
    p.add_argument('--capsule',type=Path);p.add_argument('--output',type=Path)
    args=p.parse_args();raw=args.reader.read_bytes();index=json.loads(args.index.read_bytes())
    assert sha(raw)==index['reader_sha256'] and len(raw)==index['reader_bytes']
    root=ET.fromstring(raw);assert root.tag=='repomix'
    rows=index['members'];nodes=list(root.find('files'));assert len(rows)==len(nodes)==index['member_count']
    seen=set();text_count=0;binary_count=0;line_count=1;previous_offset=0
    for row,node in zip(rows,nodes):
        path=row['path'];rel=PurePosixPath(path)
        assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in path and path.casefold() not in seen
        seen.add(path.casefold())
        for key in ('id','path','kind','bytes','sha256','encoding'):assert str(row[key])==node.attrib[key],(path,key)
        pos=row['reader_position'];segment=raw[pos['byte_start']:pos['byte_end_exclusive']]
        assert segment.startswith(b'<file ') if node.tag=='file' else segment.startswith(b'<binary_member ')
        isolated=ET.fromstring(segment)
        assert isolated.tag==node.tag and isolated.attrib==node.attrib and isolated.text==node.text
        line_count+=raw[previous_offset:pos['byte_start']].count(b'\n')
        assert line_count==pos['line_start']
        assert line_count+segment.count(b'\n')==pos['line_end']
        previous_offset=pos['byte_start']
        if node.tag=='file':
            body=(node.text or '').encode('utf-8');assert sha(body)==row['sha256'] and len(body)==row['bytes'],path
            text_count+=1
            if args.capsule:assert body==(args.capsule/path).read_bytes(),path
        else:
            assert node.tag=='binary_member' and row['encoding']=='binary-external';binary_count+=1
            if args.capsule:
                body=(args.capsule/path).read_bytes();assert sha(body)==row['sha256'] and len(body)==row['bytes'],path
    report=dict(profile='ATLAS_READER_STATIC_VERIFICATION_V02',status='PASS',reader_sha256=sha(raw),
        reader_bytes=len(raw),members=len(rows),text_members=text_count,binary_members=binary_count,
        capsule_checked=bool(args.capsule),embedded_project_code_executed=False,provider_calls=0)
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
