#!/usr/bin/env python3
"""Bounded native PPTX metadata/link attachment and independent model inspection.

Uses only Python's standard library. Never executes text, opens URLs, or renders.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import posixpath
import re
import sys
import struct
import uuid
from urllib.parse import quote, unquote
from xml.dom import Node, minidom
from xml.sax.saxutils import escape, quoteattr
import zipfile

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
XMLNS = 'http://www.w3.org/2000/xmlns/'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
A16 = 'http://schemas.microsoft.com/office/drawing/2014/main'
DCTERMS = 'http://purl.org/dc/terms/'
G6 = 'urn:g6b3r1:native-source:v1'
EMU = 9525
DRAWABLE = {'sp', 'pic', 'cxnSp', 'graphicFrame', 'grpSp'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rounded(value):
    return math.floor(value + 0.5)


def children(node, namespace=None, local=None):
    return [child for child in node.childNodes if child.nodeType == Node.ELEMENT_NODE
            and (namespace is None or child.namespaceURI == namespace)
            and (local is None or child.localName == local)]


def descend(node, namespace, local):
    return list(node.getElementsByTagNameNS(namespace, local))


def one(node, namespace, local):
    matches = children(node, namespace, local)
    require(len(matches) == 1, f'Expected one {local}, found {len(matches)}')
    return matches[0]


def optional(node, namespace, local):
    matches = children(node, namespace, local)
    require(len(matches) <= 1, f'Duplicate {local}')
    return matches[0] if matches else None


def chain(node, *names):
    for namespace, local in names:
        node = one(node, namespace, local)
    return node


def add(node, namespace, qualified, attributes=None, before=None):
    result = node.ownerDocument.createElementNS(namespace, qualified)
    for name, value in (attributes or {}).items():
        result.setAttribute(name, str(value))
    if before is None:
        node.appendChild(result)
    else:
        node.insertBefore(result, before)
    return result


def xml(data, part):
    # Exported parts are UTF-8. Reject declarations before invoking the DOM parser.
    require(b'\x00' not in data and not re.search(br'<!\s*(DOCTYPE|ENTITY)', data, re.I),
            f'Unsafe or unsupported XML encoding/declaration: {part}')
    return minidom.parseString(data)


def serialize(document):
    # minidom.toxml does not escape attribute newlines/tabs, which XML parsers
    # normalize to spaces. Preserve alt descriptions with quoteattr instead.
    def emit(node):
        if node.nodeType == Node.DOCUMENT_NODE:
            return '<?xml version="1.0" encoding="utf-8"?>' + ''.join(emit(c) for c in node.childNodes)
        if node.nodeType == Node.ELEMENT_NODE:
            attributes = ''.join(' ' + name + '=' + quoteattr(node.getAttribute(name))
                                 for name in node.attributes.keys())
            if not node.childNodes:
                return '<' + node.tagName + attributes + '/>'
            return '<' + node.tagName + attributes + '>' + ''.join(emit(c) for c in node.childNodes) + '</' + node.tagName + '>'
        if node.nodeType == Node.TEXT_NODE:
            return escape(node.data)
        if node.nodeType == Node.CDATA_SECTION_NODE:
            return '<![CDATA[' + node.data + ']]>'
        if node.nodeType == Node.COMMENT_NODE:
            return '<!--' + node.data + '-->'
        if node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
            return '<?' + node.target + (' ' + node.data if node.data else '') + '?>'
        raise ValueError(f'Unsupported XML node type: {node.nodeType}')
    return emit(document).encode('utf-8')


def strict_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def source_file(root, name):
    require(isinstance(name, str) and name and not re.search(r'[\\\x00-\x1f\x7f:?#]', name)
            and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')),
            f'Unsafe manifest-relative source path: {name}')
    current = root
    for component in name.split('/'):
        current = current / component
        require(not current.is_symlink(), f'Symlink source forbidden: {name}')
    require(current.is_file() and current.resolve().is_relative_to(root), f'Not a regular in-bundle source file: {name}')
    return current


def local_link(value, model_name):
    require(isinstance(value, str) and value, 'Missing local hyperlink')
    raw_path, separator, raw_fragment = value.partition('#')
    require(raw_path and not raw_path.startswith('/') and not re.search(r'[\\\x00-\x1f\x7f:?]', raw_path),
            f'Invalid relative file hyperlink: {value}')
    require(not re.search(r'%(?:2f|5c)', raw_path, re.I), f'Encoded path separator: {value}')
    require(not any(re.search(r'%(?![0-9a-fA-F]{2})', part) for part in (raw_path, raw_fragment)),
            f'Malformed URI encoding: {value}')
    decoded = unquote(raw_path, errors='strict')
    fragment = unquote(raw_fragment, errors='strict')
    require(not decoded.startswith('/') and not re.search(r'[\\\x00-\x1f\x7f:?#]', decoded)
            and not re.search(r'%[0-9a-fA-F]{2}', decoded), f'Unsafe/multiply encoded hyperlink: {value}')
    require(not re.search(r'[\x00-\x1f\x7f]', fragment), f'Invalid fragment: {value}')
    directory = posixpath.dirname(model_name)
    components = directory.split('/') if directory else []
    for component in decoded.split('/'):
        require(component, f'Empty local path component: {value}')
        if component == '.':
            continue
        if component == '..':
            require(components, f'Local hyperlink traverses outside handoff: {value}')
            components.pop()
        else:
            components.append(component)
    name = '/'.join(components)
    require(name, f'Local hyperlink must target a file: {value}')
    relative = posixpath.relpath(name, directory or '.')
    require(relative != '.', f'Local hyperlink targets the presentation directory: {value}')
    uri = '/'.join(quote(part, safe='-._~') for part in relative.split('/'))
    if separator:
        uri += '#' + quote(fragment, safe=";/?:@&=+$,-_.!~*'()")
    return {'uri': uri, 'source_path': name}


def planned_local_links(plan):
    targets = {obj['resolved_link'] for slide in plan['slides'] for obj in slide['objects'] if 'resolved_link' in obj}
    targets.update(ref['url'] for slide in plan['slides'] for ref in slide.get('resolved_refs', []))
    targets = {target for target in targets if not target.startswith('https://')}
    bindings = plan.get('local_links', [])
    require(len({b['uri'] for b in bindings}) == len(bindings), 'Duplicate local hyperlink binding')
    require({b['uri'] for b in bindings} == targets, 'Missing or unused manifest-bound local hyperlink')
    if bindings:
        require(plan['final_pptx_path'] == posixpath.join(posixpath.dirname(plan['model_path']), 'main.pptx'),
                'Relative hyperlinks require final main.pptx beside the model')
    for binding in bindings:
        parsed = local_link(binding['uri'], plan['model_path'])
        require(parsed['uri'] == binding['uri'] and parsed['source_path'] == binding['source_path'],
                'Local hyperlink does not match its in-bundle source binding')
    return bindings


def verify_local_sources(plan, root):
    """Check bundle bytes without opening a hyperlink or resolving it in a viewer."""
    root = root.resolve(strict=True)
    manifest_bytes = source_file(root, plan['manifest_path']).read_bytes()
    require(digest(manifest_bytes) == plan['manifest_sha256'], 'SOURCE_MANIFEST hash differs from export plan')
    manifest = strict_json(manifest_bytes)
    require(manifest['schema_version'] == 'g6b3r1-source-manifest-v1', 'Unsupported source manifest')
    rows = {row['path']: row for row in manifest['files']}
    require(len(rows) == len(manifest['files']), 'Duplicate manifest source row')
    model_bytes = source_file(root, plan['model_path']).read_bytes()
    require(digest(model_bytes) == plan['model_sha256'] and strict_json(model_bytes) == plan['model'],
            'Source model differs from export plan')
    model_row = rows.get(plan['model_path'])
    require(model_row and model_row['bytes'] == len(model_bytes) and model_row['sha256'] == digest(model_bytes),
            'Model is not manifest-bound')
    bindings = planned_local_links(plan)
    for binding in bindings:
        row = rows.get(binding['source_path'])
        require(row and row['bytes'] == binding['bytes'] and row['sha256'] == binding['sha256'],
                f'Local hyperlink target not bound to SOURCE_MANIFEST: {binding["source_path"]}')
        data = source_file(root, binding['source_path']).read_bytes()
        require(len(data) == row['bytes'] and digest(data) == row['sha256'],
                f'Local hyperlink target bytes differ: {binding["source_path"]}')
    return {'local_links_verified': len(bindings), 'relative_link_base': plan['final_pptx_path'],
            'scope': 'Regular files and manifest bytes checked; fragment/viewer navigation not executed.'}


def load_package(filename):
    with zipfile.ZipFile(filename) as archive:
        entries = archive.infolist()
        require(len(entries) <= 10000 and sum(e.file_size for e in entries) <= 512 * 1024 * 1024,
                'Package exceeds bounded inspection limits')
        require(len({e.filename for e in entries}) == len(entries), 'Duplicate ZIP part')
        for entry in entries:
            require(not entry.is_dir() and not entry.filename.startswith('/')
                    and '\\' not in entry.filename
                    and all(p not in ('', '.', '..') for p in entry.filename.split('/')),
                    f'Unsafe ZIP part: {entry.filename}')
        require(archive.testzip() is None, 'ZIP CRC failure')
        return {e.filename: archive.read(e.filename) for e in entries}


def relationship_part(part):
    folder, filename = posixpath.split(part)
    return posixpath.join(folder, '_rels', filename + '.rels')


def target_part(part, target):
    result = posixpath.normpath(target.lstrip('/') if target.startswith('/')
                              else posixpath.join(posixpath.dirname(part), target))
    require(result not in ('', '.', '..') and not result.startswith('../')
            and '\\' not in result, f'Unsafe internal relationship: {target}')
    return result


def relationships(package, part):
    name = relationship_part(part)
    require(name in package, f'Missing relationships: {name}')
    document = xml(package[name], name)
    root = document.documentElement
    require(root.namespaceURI == REL and root.localName == 'Relationships', f'Invalid relationships: {name}')
    items = {}
    for item in children(root):
        require(item.namespaceURI == REL and item.localName == 'Relationship', f'Unknown relationship entry: {name}')
        identifier = item.getAttribute('Id')
        require(identifier and identifier not in items, f'Duplicate/missing relationship id: {name}')
        items[identifier] = item
    return document, items


def related_part(package, part, kind):
    _, entries = relationships(package, part)
    matches = [entry for entry in entries.values() if entry.getAttribute('Type') == R + '/' + kind]
    require(len(matches) == 1 and matches[0].getAttribute('TargetMode') != 'External',
            f'Expected one internal {kind} relationship: {part}')
    target = target_part(part, matches[0].getAttribute('Target'))
    require(target in package, f'Missing {kind} part: {target}')
    return target


def slide_parts(package):
    document = xml(package['ppt/presentation.xml'], 'ppt/presentation.xml')
    root = document.documentElement
    size = one(root, P, 'sldSz')
    require(size.getAttribute('cx') == '12192000' and size.getAttribute('cy') == '6858000',
            'Canvas is not 1280x720 CSS px / 12192000x6858000 EMU')
    _, entries = relationships(package, 'ppt/presentation.xml')
    parts = []
    for slide in children(one(root, P, 'sldIdLst'), P, 'sldId'):
        entry = entries.get(slide.getAttributeNS(R, 'id'))
        require(entry is not None and entry.getAttribute('Type') == R + '/slide'
                and entry.getAttribute('TargetMode') != 'External', 'Invalid native slide relationship')
        part = target_part('ppt/presentation.xml', entry.getAttribute('Target'))
        require(part in package and part not in parts, 'Missing/duplicate slide part')
        parts.append(part)
    actual = {name for name in package if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)}
    require(set(parts) == actual, 'Unreferenced or nonstandard slide parts')
    return parts


def properties(element):
    container = {'sp': 'nvSpPr', 'pic': 'nvPicPr', 'cxnSp': 'nvCxnSpPr'}
    require(element.localName in container, f'Unexpected native object: {element.localName}')
    return chain(element, (P, container[element.localName]), (P, 'cNvPr'))


def native_objects(root):
    tree = chain(root, (P, 'cSld'), (P, 'spTree'))
    result = [item for item in children(tree) if item.namespaceURI == P and item.localName in DRAWABLE]
    require(all(item.localName in ('sp', 'pic', 'cxnSp') for item in result), 'Grouped, flattened or unsupported object')
    return tree, result


def box(element):
    transform = chain(element, (P, 'spPr'), (A, 'xfrm'))
    origin, size = one(transform, A, 'off'), one(transform, A, 'ext')
    return [int(origin.getAttribute('x')), int(origin.getAttribute('y')),
            int(size.getAttribute('cx')), int(size.getAttribute('cy'))]


def expected_box(obj):
    values = [obj[key] for key in ('x', 'y', 'w', 'h')]
    if obj['kind'] in ('line', 'arrow'):
        values = [min(obj['x'], obj['x'] + obj['w']), min(obj['y'], obj['y'] + obj['h']), abs(obj['w']), abs(obj['h'])]
    return [rounded(value * EMU) for value in values]


def contained_image_box(obj, data):
    """Reconstruct contain-fit geometry from authenticated raster dimensions."""
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        require(len(data) >= 24 and data[12:16] == b'IHDR', 'Invalid PNG dimensions')
        iw, ih = struct.unpack('>II', data[16:24])
    else:
        require(data.startswith(b'\xff\xd8'), 'Unsupported raster format')
        pos = 2; iw = ih = 0
        while pos < len(data):
            require(data[pos] == 255, 'Malformed JPEG marker')
            while pos < len(data) and data[pos] == 255:
                pos += 1
            require(pos < len(data), 'Truncated JPEG marker')
            marker = data[pos]; pos += 1
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                continue
            require(marker not in (0xD9, 0xDA) and pos + 2 <= len(data), 'JPEG dimensions missing')
            length = int.from_bytes(data[pos:pos + 2], 'big')
            require(length >= 2 and pos + length <= len(data), 'Invalid JPEG segment')
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                require(length >= 8, 'Truncated JPEG frame')
                ih, iw = struct.unpack('>HH', data[pos + 3:pos + 7]); break
            pos += length
    require(iw > 0 and ih > 0, 'Nonpositive raster dimensions')
    scale = min(obj['w'] / iw, obj['h'] / ih)
    w, h = iw * scale, ih * scale
    return [rounded(v * EMU) for v in (obj['x'] + (obj['w'] - w) / 2,
            obj['y'] + (obj['h'] - h) / 2, w, h)]


def check_box(element, obj, raster=None):
    expected = contained_image_box(obj, raster) if obj['kind'] == 'image' and raster is not None else expected_box(obj)
    require(all(abs(a - b) <= 1 for a, b in zip(box(element), expected)),
            f'{obj["id"]}: native geometry differs: {box(element)} != {expected}')
    transform = chain(element, (P, 'spPr'), (A, 'xfrm'))
    require(transform.getAttribute('rot') in ('', '0'), f'{obj["id"]}: unexpected rotation')


def set_line_geometry(element, obj):
    """Encode exact straight line geometry, including legitimate zero extents."""
    sppr = one(element, P, 'spPr')
    transform = optional(sppr, A, 'xfrm')
    if transform is None:
        transform = add(sppr, A, 'a:xfrm', before=sppr.firstChild)
    origin = optional(transform, A, 'off')
    size = optional(transform, A, 'ext')
    if origin is None:
        origin = add(transform, A, 'a:off', before=transform.firstChild)
    if size is None:
        size = add(transform, A, 'a:ext')
    x, y, w, h = expected_box(obj)
    for name, value in [('x', x), ('y', y)]:
        origin.setAttribute(name, str(value))
    for name, value in [('cx', w), ('cy', h)]:
        size.setAttribute(name, str(value))
    transform.setAttribute('rot', '0')
    start = obj.get('route', {}).get('start', [obj['x'], obj['y']])
    end = obj.get('route', {}).get('end', [obj['x'] + obj['w'], obj['y'] + obj['h']])
    transform.setAttribute('flipH', '1' if end[0] < start[0] else '0')
    transform.setAttribute('flipV', '1' if end[1] < start[1] else '0')


def connector_endpoints(element):
    config = chain(element, (P, 'nvCxnSpPr'), (P, 'cNvCxnSpPr'))
    return one(config, A, 'stCxn'), one(config, A, 'endCxn')


def check_route(element, obj, ids):
    require(element.localName == 'cxnSp', f'{obj["id"]}: arrow must be native p:cxnSp')
    if obj['route'].get('unconnected'):
        config = chain(element, (P, 'nvCxnSpPr'), (P, 'cNvCxnSpPr'))
        require(not children(config, A, 'stCxn') and not children(config, A, 'endCxn'),
                f'{obj["id"]}: comparison arrow must not acquire endpoint references')
        return
    start, end = connector_endpoints(element)
    require(start.getAttribute('id') == ids[obj['source_id']] and end.getAttribute('id') == ids[obj['target_id']],
            f'{obj["id"]}: connector endpoint ownership differs')
    require(start.getAttribute('idx') == str(obj['route']['fromIdx'])
            and end.getAttribute('idx') == str(obj['route']['toIdx']), f'{obj["id"]}: connector site differs')


def promote_free_arrow(element):
    """The API documents unattached lines, not unattached connector construction."""
    document = element.ownerDocument
    if element.localName == 'sp':
        body = optional(element, P, 'txBody')
        if body is not None:
            require(not text_content(body), 'Cannot convert a text-bearing shape to a comparison connector')
            element.removeChild(body)
        native = one(element, P, 'nvSpPr')
        config = one(native, P, 'cNvSpPr')
        if config.hasAttribute('txBox'):
            config.removeAttribute('txBox')
        document.renameNode(config, P, 'p:cNvCxnSpPr')
        document.renameNode(native, P, 'p:nvCxnSpPr')
        document.renameNode(element, P, 'p:cxnSp')
    require(element.localName == 'cxnSp', 'Comparison arrow must originate as a native line')
    config = chain(element, (P, 'nvCxnSpPr'), (P, 'cNvCxnSpPr'))
    require(not children(config, A, 'stCxn') and not children(config, A, 'endCxn'), 'Unexpected attached comparison arrow')
    sppr = one(element, P, 'spPr')
    require(one(sppr, A, 'prstGeom').getAttribute('prst') in ('line', 'straightConnector1'), 'Comparison arrow must originate as a straight line')
    line = one(sppr, A, 'ln')
    tail = optional(line, A, 'tailEnd')
    if tail is None:
        tail = add(line, A, 'a:tailEnd', before=optional(line, A, 'extLst'))
    for name, value in [('type', 'triangle'), ('w', 'med'), ('len', 'med')]:
        tail.setAttribute(name, value)


def exact_line_height(element, obj):
    body = one(element, P, 'txBody')
    one(body, A, 'bodyPr').setAttribute('anchor', 't')
    if 'line_height_px' not in obj:
        return
    for paragraph in children(body, A, 'p'):
        style = optional(paragraph, A, 'pPr')
        if style is None:
            style = add(paragraph, A, 'a:pPr', before=paragraph.firstChild)
        for local in ('lnSpc', 'spcBef', 'spcAft'):
            old = optional(style, A, local)
            if old is not None:
                style.removeChild(old)
        boundary = style.firstChild
        for local, value in [('lnSpc', rounded(obj['line_height_px'] * 75)), ('spcBef', 0), ('spcAft', 0)]:
            spacing = add(style, A, 'a:' + local, before=boundary)
            add(spacing, A, 'a:spcPts', {'val': value})


def source_metadata(parent, value, namespace, prefix):
    extension_list = optional(parent, namespace, 'extLst')
    if extension_list is None:
        extension_list = add(parent, namespace, prefix + ':extLst')
    require(not any(e.getAttribute('uri') == G6 for e in children(extension_list)), 'Duplicate source metadata')
    extension = add(extension_list, namespace, prefix + ':ext', {'uri': G6})
    data = add(extension, G6, 'g6:source')
    data.setAttributeNS(XMLNS, 'xmlns:g6', G6)
    data.appendChild(parent.ownerDocument.createTextNode(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)))


def check_metadata(parent, value, namespace):
    extensions = children(one(parent, namespace, 'extLst'), namespace, 'ext')
    matches = [element for element in extensions if element.getAttribute('uri') == G6]
    require(len(matches) == 1, 'Source metadata missing/duplicated')
    data = one(matches[0], G6, 'source')
    text = ''.join(c.data for c in data.childNodes if c.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE))
    require(strict_json(text) == value, 'Exact source metadata differs')


def image_bytes(package, part, element):
    fill = one(element, P, 'blipFill')
    blip = one(fill, A, 'blip')
    require(not blip.getAttributeNS(R, 'link'), 'Externally linked image forbidden')
    _, entries = relationships(package, part)
    entry = entries.get(blip.getAttributeNS(R, 'embed'))
    require(entry is not None and entry.getAttribute('Type') == R + '/image'
            and entry.getAttribute('TargetMode') != 'External', 'Image must be embedded natively')
    target = target_part(part, entry.getAttribute('Target'))
    require(target in package, f'Missing image bytes: {target}')
    data = package[target]
    require(data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8\xff'), 'Only original raster PNG/JPEG images are allowed')
    require(not descend(element, 'http://schemas.microsoft.com/office/drawing/2016/SVG/main', 'svgBlip'), 'Flattened SVG forbidden')
    return data


def text_content(body):
    paragraphs = []
    for paragraph in children(body, A, 'p'):
        fragments = []
        for item in children(paragraph):
            if item.namespaceURI == A and item.localName in ('r', 'fld'):
                node = one(item, A, 't')
                fragments.append(''.join(c.data for c in node.childNodes if c.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE)))
            elif item.namespaceURI == A and item.localName == 'br':
                fragments.append('\n')
        paragraphs.append(''.join(fragments))
    return '\n'.join(paragraphs)


def notes_body(document):
    bodies = []
    for shape in descend(document, P, 'sp'):
        placeholders = descend(shape, P, 'ph')
        if any(ph.getAttribute('type') == 'body' for ph in placeholders):
            bodies.append(one(shape, P, 'txBody'))
    require(len(bodies) == 1, f'Expected one native notes body, found {len(bodies)}')
    return bodies[0]


def explicit_notes_font(document):
    root = document.documentElement
    root.setAttributeNS(XMLNS, 'xmlns:a', A)
    for run in descend(notes_body(document), A, 'r'):
        style = optional(run, A, 'rPr')
        if style is None:
            style = add(run, A, 'a:rPr', before=run.firstChild)
        style.setAttribute('lang', 'ru-RU')
        for local in ('latin', 'ea', 'cs'):
            existing = optional(style, A, local)
            if existing is not None:
                style.removeChild(existing)
        boundary = next((n for n in children(style) if n.localName in ('sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst')), None)
        for local in ('latin', 'ea', 'cs'):
            add(style, A, 'a:' + local, {'typeface': 'Nimbus Sans'}, before=boundary)


def check_paint(parent, expected, label):
    if expected == 'none':
        require(optional(parent, A, 'noFill') is not None, label + ': noFill missing')
    else:
        color = chain(parent, (A, 'solidFill'), (A, 'srgbClr'))
        require(color.getAttribute('val').upper() == expected[1:].upper(), label + ': color differs')
        require(not children(color), label + ': unexpected opacity/color transform')


def check_style(element, obj):
    sppr = one(element, P, 'spPr')
    if obj['kind'] == 'text':
        body = one(element, P, 'txBody')
        require(text_content(body) == obj['text'], f'{obj["id"]}: exact text differs')
        runs = descend(body, A, 'r')
        require(runs, f'{obj["id"]}: no editable text runs')
        for run in runs:
            # Artifact Tool emits an unstyled zero-glyph run for a deliberate blank line.
            # Exact text and explicit paragraph spacing are checked independently.
            if not any(text.firstChild and text.firstChild.data for text in children(run, A, 't')):
                continue
            style = one(run, A, 'rPr')
            require(style.getAttribute('sz') == str(rounded(obj['font_px'] * 75)), f'{obj["id"]}: explicit CSS-px font size differs/missing')
            require(one(style, A, 'latin').getAttribute('typeface') == 'Nimbus Sans', f'{obj["id"]}: exact Nimbus Sans missing')
            require((style.getAttribute('b') in ('1', 'true')) == obj['bold'], f'{obj["id"]}: bold differs')
            check_paint(style, obj['color'], obj['id'])
        alignment = {'left': 'l', 'center': 'ctr', 'right': 'r', 'justify': 'just'}[obj.get('align', 'left')]
        for paragraph in children(body, A, 'p'):
            style = optional(paragraph, A, 'pPr')
            actual = (style.getAttribute('algn') or 'l') if style is not None else 'l'
            require(actual == alignment, f'{obj["id"]}: text alignment differs')
        bodypr = one(body, A, 'bodyPr')
        require(bodypr.getAttribute('anchor') == 't', f'{obj["id"]}: native top text anchor missing')
        require(all(bodypr.getAttribute(key) == '0' for key in ('lIns', 'rIns', 'tIns', 'bIns')), f'{obj["id"]}: text insets differ/missing')
        require(bodypr.getAttribute('wrap') == 'none', f'{obj["id"]}: unexpected automatic text wrap')
        require(not children(bodypr, A, 'normAutofit') and not children(bodypr, A, 'spAutoFit'), f'{obj["id"]}: forbidden font/shape auto-fit')
        if 'line_height_px' in obj:
            for paragraph in children(body, A, 'p'):
                style = one(paragraph, A, 'pPr')
                for local, value in [('lnSpc', rounded(obj['line_height_px'] * 75)), ('spcBef', 0), ('spcAft', 0)]:
                    require(chain(style, (A, local), (A, 'spcPts')).getAttribute('val') == str(value), f'{obj["id"]}: exact paragraph spacing differs')
    elif obj['kind'] in ('rect', 'ellipse'):
        require(one(sppr, A, 'prstGeom').getAttribute('prst') == obj['kind'], f'{obj["id"]}: shape preset differs')
        check_paint(sppr, obj['fill'], obj['id'])
    elif obj['kind'] in ('line', 'arrow'):
        geometry = one(sppr, A, 'prstGeom').getAttribute('prst')
        require(geometry in ('line', 'straightConnector1'), f'{obj["id"]}: native straight line required')
    if obj['kind'] in ('rect', 'ellipse', 'line', 'arrow'):
        line = one(sppr, A, 'ln')
        require(abs(int(line.getAttribute('w') or 0) - rounded(obj['stroke_width'] * EMU)) <= 1, f'{obj["id"]}: stroke width differs')
        check_paint(line, obj.get('stroke', obj.get('color')), obj['id'])
        tail, head = optional(line, A, 'tailEnd'), optional(line, A, 'headEnd')
        if obj['kind'] == 'arrow':
            require(tail is not None and tail.getAttribute('type') == 'triangle', f'{obj["id"]}: destination triangle arrowhead missing')
        else:
            require(tail is None or tail.getAttribute('type') in ('', 'none'), f'{obj["id"]}: unexpected arrowhead')
        require(head is None or head.getAttribute('type') in ('', 'none'), f'{obj["id"]}: unexpected source arrowhead')


def map_draft(package, part, root, slide):
    _, native = native_objects(root)
    require(len(native) == len(slide['objects']), f'{slide["id"]}: native object count differs')
    mapped, used = {}, set()
    for obj in slide['objects']:
        if obj['kind'] == 'image' or (obj['kind'] == 'arrow' and not obj['route'].get('unconnected')):
            continue
        matches = [item for item in native if properties(item).getAttribute('name') == obj['id']]
        require(len(matches) == 1, f'{obj["id"]}: supported shape name did not survive export')
        element = matches[0]
        require(element.localName == 'sp' or (obj['kind'] in ('line', 'arrow') and element.localName == 'cxnSp'), f'{obj["id"]}: wrong native type')
        mapped[obj['id']] = element; used.add(id(element))
    ids = {name: properties(element).getAttribute('id') for name, element in mapped.items()}
    for obj in slide['objects']:
        if obj['id'] in mapped:
            continue
        candidates = []
        for element in native:
            if id(element) in used:
                continue
            try:
                if obj['kind'] == 'arrow':
                    check_route(element, obj, ids)
                    check_style(element, obj)
                else:
                    require(element.localName == 'pic', 'Not a picture')
                    require(properties(element).getAttribute('descr') in ('', obj['alt']), 'Image alt differs')
                    raster = image_bytes(package, part, element)
                    require(digest(raster) == obj['media_sha256'], 'Image bytes differ')
                    check_box(element, obj, raster)
                candidates.append(element)
            except (ValueError, KeyError):
                continue
        require(candidates, f'{obj["id"]}: cannot identify exact native {obj["kind"]}; no fabricated substitute')
        # Repeated indistinguishable native objects are assigned in XML order.
        element = candidates[0]
        mapped[obj['id']] = element; used.add(id(element))
    require(len(used) == len(native), 'Unmapped native objects')
    return mapped


def attach(package, plan):
    planned_local_links(plan)
    result = dict(package)
    parts = slide_parts(package)
    require(len(parts) == len(plan['slides']), 'Slide count differs from model')
    changes = []
    presentation = xml(package['ppt/presentation.xml'], 'ppt/presentation.xml')
    presentation.documentElement.setAttributeNS(XMLNS, 'xmlns:p', P)
    source_metadata(presentation.documentElement, {k: v for k, v in plan['model'].items() if k != 'slides'}, P, 'p')
    result['ppt/presentation.xml'] = serialize(presentation)
    changes.append('ppt/presentation.xml')
    for part, slide, source_slide in zip(parts, plan['slides'], plan['model']['slides']):
        document = xml(package[part], part); root = document.documentElement
        root.setAttributeNS(XMLNS, 'xmlns:a', A); root.setAttributeNS(XMLNS, 'xmlns:r', R)
        tree, native = native_objects(root)
        mapped = map_draft(package, part, root, slide)
        oldids = [properties(item).getAttribute('id') for item in native]
        require(len(set(oldids)) == len(oldids) and all(x.isdigit() for x in oldids), 'Invalid native drawing ids')
        group_props = chain(tree, (P, 'nvGrpSpPr'), (P, 'cNvPr'))
        group_props.setAttribute('id', '1')
        newid = {obj['id']: str(index + 2) for index, obj in enumerate(slide['objects'])}
        rel_doc, entries = relationships(package, part)
        require(not any(e.getAttribute('Type') == R + '/hyperlink' for e in entries.values()), 'Draft already contains hyperlinks; refusing duplicate attachment')
        rel_root = rel_doc.documentElement
        for index, obj in enumerate(slide['objects']):
            element = mapped[obj['id']]; props = properties(element)
            require(not descend(element, A, 'hlinkClick') and not descend(element, A, 'hlinkMouseOver'), 'Draft already has native links')
            props.setAttribute('id', newid[obj['id']]); props.setAttribute('name', obj['id']); props.setAttribute('descr', obj['alt'])
            if obj['kind'] == 'arrow':
                if obj['route'].get('unconnected'):
                    promote_free_arrow(element)
                else:
                    start, end = connector_endpoints(element)
                    start.setAttribute('id', newid[obj['source_id']]); end.setAttribute('id', newid[obj['target_id']])
                set_line_geometry(element, obj)
            elif obj['kind'] == 'line':
                set_line_geometry(element, obj)
            elif obj['kind'] == 'text':
                exact_line_height(element, obj)
            if 'resolved_link' in obj:
                identifier = f'g6b3r1Link{index + 1}'
                require(identifier not in entries, 'Relationship id collision')
                boundary = next((node for node in children(props) if node.localName in ('hlinkMouseOver', 'extLst')), None)
                link = add(props, A, 'a:hlinkClick', before=boundary)
                link.setAttributeNS(R, 'r:id', identifier)
                qualified = (rel_root.prefix + ':' if rel_root.prefix else '') + 'Relationship'
                add(rel_root, REL, qualified, {'Id': identifier, 'Type': R + '/hyperlink',
                    'Target': obj['resolved_link'], 'TargetMode': 'External'})
            source_metadata(props, source_slide['objects'][index], A, 'a')
        for element in native:
            tree.removeChild(element)
        boundary = optional(tree, P, 'extLst')
        for obj in slide['objects']:
            if boundary is None:
                tree.appendChild(mapped[obj['id']])
            else:
                tree.insertBefore(mapped[obj['id']], boundary)
        one(root, P, 'cSld').setAttribute('name', slide['id'])
        source_metadata(one(root, P, 'cSld'), {k: v for k, v in source_slide.items() if k != 'objects'}, P, 'p')
        result[part] = serialize(document)
        result[relationship_part(part)] = serialize(rel_doc)
        notes = related_part(package, part, 'notesSlide')
        notes_doc = xml(package[notes], notes)
        require(text_content(notes_body(notes_doc)) == slide['exported_notes'], f'{slide["id"]}: API notes differ; refusing text repair')
        explicit_notes_font(notes_doc); result[notes] = serialize(notes_doc)
        changes.extend([part, relationship_part(part), notes])
    # Stabilize known producer-generated identity/time fields, not slide content.
    for part, payload in list(result.items()):
        if not part.endswith('.xml'):
            continue
        document = xml(payload, part); dirty = False
        for namespace in (P14, A16):
            for index, element in enumerate(descend(document, namespace, 'creationId')):
                seed = f'{plan["model_sha256"]}/{part}/{namespace}/{index}'
                if namespace == P14:
                    element.setAttribute('val', str(int(digest(seed.encode())[:8], 16)))
                else:
                    element.setAttribute('id', '{' + str(uuid.uuid5(uuid.NAMESPACE_URL, seed)).upper() + '}')
                dirty = True
        if part == 'docProps/core.xml':
            for local in ('created', 'modified'):
                for element in descend(document, DCTERMS, local):
                    while element.firstChild:
                        element.removeChild(element.firstChild)
                    element.appendChild(document.createTextNode('2000-01-01T00:00:00Z')); dirty = True
        if dirty:
            result[part] = serialize(document); changes.append(part)
    return result, sorted(set(changes))


def inspect(package, plan):
    bindings = planned_local_links(plan)
    parts = slide_parts(package)
    presentation = xml(package['ppt/presentation.xml'], 'ppt/presentation.xml')
    check_metadata(presentation.documentElement, {k: v for k, v in plan['model'].items() if k != 'slides'}, P)
    require(len(parts) == len(plan['slides']), 'Native slide count differs')
    report = []
    notes_seen = set()
    for part, slide, source_slide in zip(parts, plan['slides'], plan['model']['slides']):
        root = xml(package[part], part).documentElement
        require(one(root, P, 'cSld').getAttribute('name') == slide['id'], f'{slide["id"]}: stable slide name missing')
        check_metadata(one(root, P, 'cSld'), {k: v for k, v in source_slide.items() if k != 'objects'}, P)
        _, native = native_objects(root)
        require(len(native) == len(slide['objects']), f'{slide["id"]}: wrong native object count')
        names = [properties(item).getAttribute('name') for item in native]
        require(names == [obj['id'] for obj in slide['objects']], f'{slide["id"]}: reading order/names differ')
        ids = {name: properties(element).getAttribute('id') for name, element in zip(names, native)}
        require(list(ids.values()) == [str(i + 2) for i in range(len(native))], 'Unstable native drawing ids')
        _, entries = relationships(package, part)
        link_ids = set()
        for element, obj, source_obj in zip(native, slide['objects'], source_slide['objects']):
            require(properties(element).getAttribute('descr') == obj['alt'], f'{obj["id"]}: alt differs')
            check_metadata(properties(element), source_obj, A)
            if obj['kind'] == 'image':
                require(element.localName == 'pic', f'{obj["id"]}: image is not native p:pic')
                raster = image_bytes(package, part, element)
                require(digest(raster) == obj['media_sha256'], f'{obj["id"]}: original bitmap bytes differ')
                check_box(element, obj, raster)
            else:
                check_box(element, obj)
                require(element.localName == ('cxnSp' if obj['kind'] == 'arrow' else 'sp')
                        or (obj['kind'] == 'line' and element.localName == 'cxnSp'), f'{obj["id"]}: native kind differs')
                check_style(element, obj)
            if obj['kind'] == 'arrow':
                check_route(element, obj, ids)
            if obj['kind'] in ('line', 'arrow'):
                transform = chain(element, (P, 'spPr'), (A, 'xfrm'))
                start = obj.get('route', {}).get('start', [obj['x'], obj['y']])
                end = obj.get('route', {}).get('end', [obj['x'] + obj['w'], obj['y'] + obj['h']])
                for key, axis in [('flipH', 0), ('flipV', 1)]:
                    require((transform.getAttribute(key) in ('1', 'true')) == (end[axis] < start[axis]), f'{obj["id"]}: line/arrow direction differs')
            links = descend(element, A, 'hlinkClick')
            require(not descend(element, A, 'hlinkMouseOver'), 'Unexpected hover link')
            if 'resolved_link' in obj:
                require(len(links) == 1 and links[0].parentNode is properties(element), f'{obj["id"]}: missing/duplicate shape hyperlink')
                identifier = links[0].getAttributeNS(R, 'id'); link_ids.add(identifier)
                rel = entries.get(identifier)
                require(rel is not None and rel.getAttribute('Type') == R + '/hyperlink'
                        and rel.getAttribute('TargetMode') == 'External'
                        and rel.getAttribute('Target') == obj['resolved_link'], f'{obj["id"]}: exact hyperlink target differs')
            else:
                require(not links, f'{obj["id"]}: unexpected hyperlink')
        actual_links = {key for key, value in entries.items() if value.getAttribute('Type') == R + '/hyperlink'}
        require(actual_links == link_ids, 'Missing or orphaned hyperlink relationship')
        notes = related_part(package, part, 'notesSlide')
        require(notes not in notes_seen, 'Shared notes part'); notes_seen.add(notes)
        body = notes_body(xml(package[notes], notes))
        require(text_content(body) == slide['exported_notes'], f'{slide["id"]}: exact Russian notes/source references differ')
        for run in descend(body, A, 'r'):
            require(one(one(run, A, 'rPr'), A, 'latin').getAttribute('typeface') == 'Nimbus Sans', 'Notes font differs')
        report.append({'id': slide['id'], 'title': slide['title'], 'native_types': dict(Counter(e.localName for e in native)),
                       'model_kinds': dict(Counter(o['kind'] for o in slide['objects'])),
                       'object_count': len(native), 'hyperlinks': len(link_ids), 'notes_sha256': digest(slide['exported_notes'].encode())})
    actual_notes = {part for part in package if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', part)}
    require(actual_notes == notes_seen, 'Unexpected or missing native notes part')
    return {'status': 'NATIVE_STRUCTURE_MATCHES_MODEL_VISUAL_REVIEW_PENDING',
            'canvas_emu': [12192000, 6858000], 'slides': report,
            'model_sha256': plan['model_sha256'], 'manifest_sha256': plan['manifest_sha256'],
            'presentation_metadata': {k: v for k, v in plan['model'].items() if k != 'slides'},
            'local_hyperlink_count': len(bindings),
            'limits': ['Not visual QA, viewer/fragment navigation, remote link availability, PowerPoint desktop validation, font embedding, B4 acceptance or owner landing.',
                       'Byte-for-byte reproducibility across independent Work exports remains to be measured.']}


def write_package(filename, package):
    with zipfile.ZipFile(filename, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(package):
            info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3; info.external_attr = 0o100644 << 16
            archive.writestr(info, package[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['attach', 'inspect'])
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--presentation-root', required=True, type=Path)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    require(args.report.resolve() != args.input.resolve() and not args.report.exists(), 'Report must be a new file')
    require((args.mode == 'attach') == (args.output is not None), '--output is required only for attach')
    if args.output:
        require(not args.output.exists() and args.output.resolve() not in (args.input.resolve(), args.report.resolve(), args.plan.resolve()), 'Output must be a distinct new file')
    plan = strict_json(args.plan.read_bytes())
    require(plan['schema_version'] == 'g6b3r1-export-plan-v1', 'Unsupported export plan')
    source_check = verify_local_sources(plan, args.presentation_root)
    package = load_package(args.input)
    input_sha = digest(args.input.read_bytes())
    changes = []
    if args.mode == 'attach':
        package, changes = attach(package, plan)
    report = inspect(package, plan)
    if args.output:
        write_package(args.output, package)
        inspect(load_package(args.output), plan)
    final = args.output or args.input
    report.update({'input_sha256': input_sha, 'pptx_sha256': digest(final.read_bytes()),
                   'plan_sha256': digest(args.plan.read_bytes()), 'changed_parts': changes,
                   'bundle_links': verify_local_sources(plan, args.presentation_root)})
    require(report['bundle_links'] == source_check, 'Local source binding changed during postprocessing')
    with args.report.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'status': report['status'], 'slides': len(report['slides']), 'pptx_sha256': report['pptx_sha256']}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        print(f'G6B3R1 native package check stopped: {error}', file=sys.stderr)
        sys.exit(1)
