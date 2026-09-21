#!/usr/bin/env python3
"""Verify a Sentinel reader and optional detached inventory without executing its contents."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reader", type=Path)
parser.add_argument("--index", type=Path)
args = parser.parse_args()
data = args.reader.read_bytes()
assert not re.search(r"[\u0400-\u052f]", data.decode("utf-8")), "Cyrillic text"
root = ET.fromstring(data)
assert root.tag == "repomix"
nodes = root.findall("./files/file")
seen, observed = set(), {}
for node in nodes:
    path = node.attrib["path"]
    assert path not in seen and not Path(path).is_absolute() and ".." not in Path(path).parts, path
    seen.add(path)
    body = (node.text or "").encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()
    assert digest == node.attrib["sha256"], path
    assert len(body) == int(node.attrib["bytes"]), path
    assert len(body.decode().splitlines()) == int(node.attrib["lines"]), path
    observed[path] = dict(sha256=digest, bytes=len(body), kind=node.attrib["kind"])
if args.index:
    index = json.loads(args.index.read_text())
    assert index["reader_sha256"] == hashlib.sha256(data).hexdigest()
    assert index["reader_bytes"] == len(data)
    assert index["file_count"] == len(nodes)
    expected = {row["path"]: {key: row[key] for key in ("sha256", "bytes", "kind")}
                for row in index["file_manifest"]}
    assert observed == expected
print(json.dumps(dict(status="PASS", reader=args.reader.name, bytes=len(data),
                      sha256=hashlib.sha256(data).hexdigest(), files=len(nodes),
                      source_commit=root.attrib["commit"], embedded_code_executed=False), indent=2))
