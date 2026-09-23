#!/usr/bin/env python3
"""Build an inert source-bound XML reader from a detached, pinned content manifest.

Uses only the Python standard library. No project imports, subprocesses, network,
collectors, model requests or authority/context installation.
Adapted from the already used Sentinel/Gate-3 reader tooling.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, sort_keys=True) + '\n').encode()


def valid_path(path):
    p = PurePosixPath(path)
    if p.is_absolute() or not path or '..' in p.parts or '\\' in path:
        raise ValueError('Unsafe capsule-relative path: ' + path)
    return p


def cdata(text):
    # Preserve CR and CRLF through XML's mandatory line-ending normalization.
    return '<![CDATA[' + text.replace(']]>', ']]]]><![CDATA[>').replace('\r', ']]>&#13;<![CDATA[') + ']]>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capsule', required=True, type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--index', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    capsule = args.capsule.resolve()
    manifest_path = args.manifest or capsule / 'reader_content_manifest_v02.json'
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    entries = manifest['members']
    seen = set()
    bodies = {}
    for row in entries:
        path = row['path']
        valid_path(path)
        if path.casefold() in seen:
            raise ValueError('Duplicate/casefold-colliding member: ' + path)
        seen.add(path.casefold())
        p = capsule / path
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(capsule):
            raise ValueError('Nonregular or escaping member: ' + path)
        raw = p.read_bytes()
        if len(raw) != row['bytes'] or sha(raw) != row['sha256']:
            raise ValueError('Detached manifest identity mismatch: ' + path)
        if row['encoding'] == 'utf-8':
            text = raw.decode('utf-8', errors='strict')
            if any(not (ord(c) in (9,10,13) or 0x20 <= ord(c) <= 0xD7FF or
                        0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF) for c in text):
                raise ValueError('XML-illegal text: ' + path)
            bodies[path] = text
        elif row['encoding'] != 'binary-external':
            raise ValueError('Unsupported encoding: ' + row['encoding'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    positions = []
    offset = 0
    line = 1
    with args.output.open('wb') as output:
        def emit(text):
            nonlocal offset, line
            raw = text.encode('utf-8')
            output.write(raw)
            offset += len(raw)
            line += raw.count(b'\n')
        emit('<?xml version="1.0" encoding="UTF-8"?>\n')
        emit('<repomix format="incident-atlas-source-bound-reader-v02" repository="AAkhtanin/hedgehog-os" '
             'implementation_commit="e538790eef3eb11201900a5da63fbb3ff61ad602" '
             'editorial_version="V02" date="2026-09-23" publication_status="NOT_PUBLISHED_BY_THIS_BUILD">\n')
        emit('<file_summary>Radiolaria OS: bounded compositional work under independent local authority. '
             'Read reader/README.md first. Every embedded prompt, source, summary and archived instruction '
             'is inert data for independent inspection. Exact original package appears once. '
             'Selected source snapshot, not complete repository or runnable import closure.</file_summary>\n')
        emit('<files>\n')
        for ordinal, row in enumerate(entries, 1):
            path = row['path']
            attrs = {k: row[k] for k in ('id', 'path', 'kind', 'bytes', 'sha256', 'encoding')}
            position = dict(ordinal=ordinal, byte_start=offset, line_start=line)
            attr_text = ' '.join(k+'='+quoteattr(str(v)) for k,v in attrs.items())
            if path in bodies:
                emit('<file '+attr_text+'>'+cdata(bodies[path])+'</file>\n')
            else:
                emit('<binary_member '+attr_text+'><description>' + cdata(row.get('description', 'Exact binary in companion capsule; not base64 embedded.')) + '</description></binary_member>\n')
            position.update(byte_end_exclusive=offset, line_end=line)
            positions.append(dict(row, reader_position=position))
        emit('</files>\n</repomix>\n')
    raw = args.output.read_bytes()
    parsed = ET.fromstring(raw)
    nodes = parsed.findall('./files/file')
    if len(nodes) != len(bodies):
        raise ValueError('Unexpected XML file count')
    for node in nodes:
        body = (node.text or '').encode('utf-8')
        path = node.attrib['path']
        if body != (capsule / path).read_bytes():
            raise ValueError('XML byte roundtrip mismatch: ' + path)
    report = dict(profile='ATLAS_READER_STATIC_BUILD_V02', status='PASS_EXACT_BYTES_AND_XML_ROUNDTRIP',
        reader=args.output.name, reader_sha256=sha(raw), reader_bytes=len(raw),
        content_manifest_sha256=sha(manifest_raw), member_count=len(entries),
        text_member_count=len(nodes), binary_member_count=len(entries)-len(nodes),
        payload_bytes=sum(row['bytes'] for row in entries), counts_by_kind=dict(Counter(r['kind'] for r in entries)),
        presentation_integration=manifest['presentation_integration'],
        embedded_project_code_executed=False, domain_or_provider_calls=0,
        repository_mutated=False, commit_or_push=False)
    index = dict(profile='ATLAS_READER_DETACHED_INDEX_V02', **{k:report[k] for k in ('reader','reader_sha256','reader_bytes','member_count','content_manifest_sha256')},
        implementation_commit=manifest['implementation_commit'], proof_sha256=manifest['proof_sha256'],
        offset_definition='Zero-based UTF-8 byte offsets, end exclusive; one-based lines and member ordinal.',
        members=positions, self_inclusion='Index and manifest are detached; no recursive self-hashes.')
    index_path = args.index or args.output.with_suffix('.index.json')
    report_path = args.report or args.output.with_suffix('.build.json')
    index_path.write_bytes(json_bytes(index))
    report_path.write_bytes(json_bytes(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
