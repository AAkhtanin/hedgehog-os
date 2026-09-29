"""Synthetic XML unit tests only, not an Artifact Tool or Office export test."""
import base64
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from xml.sax.saxutils import escape, quoteattr

sys.dont_write_bytecode = True
import attach_links as native


def attrs(values):
    return ' '.join(f'{key}={quoteattr(str(value))}' for key, value in values.items())


def fixture():
    base = {'x': 20, 'y': 200, 'w': 100, 'h': 50, 'alt': 'Native object', 'reading_order': 0}
    title = dict(base, id='title', kind='text', x=20, y=20, w=1000, h=80,
                 text='Title\nExact second line', font_px=24, line_height_px=30,
                 color='#123456', bold=True, link_target='https://github.com/AAkhtanin/hedgehog-os/blob/main/README.md')
    source = dict(base, id='source', kind='rect', reading_order=1, fill='#FFFFFF', stroke='#123456', stroke_width=1)
    target = dict(source, id='target', x=300, reading_order=2)
    arrow = dict(base, id='arrow', kind='arrow', x=120, y=225, w=180, h=0, reading_order=3,
                 source_id='source', target_id='target', head='triangle', color='#123456', stroke_width=2,
                 relation_type='comparison')
    free = dict(arrow, id='free', x=40, y=350, source_id=None, target_id=None, reading_order=4)
    vertical = dict(base, id='vertical', kind='line', x=600, y=100, w=0, h=200, reading_order=5,
                    color='#123456', stroke_width=1)
    picture = dict(base, id='picture', kind='image', x=800, y=300, w=100, h=100, reading_order=6,
                   path='../assets/pixel.png', originalbitmap=True)
    ellipse = dict(source, id='ellipse', kind='ellipse', x=500, y=500, reading_order=7)
    objects = [title, source, target, arrow, free, vertical, picture, ellipse]
    source_slide = {'id': 's01', 'title': title['text'], 'notes_ru': '\u0420\u0443\u0441\u0441\u043a\u0438\u0435 \u0437\u0430\u043c\u0435\u0442\u043a\u0438.\n\u0412\u0442\u043e\u0440\u0430\u044f \u0441\u0442\u0440\u043e\u043a\u0430.',
                    'source_refs': [], 'objects': objects, 'scope': {'bounded': True},
                    'relations': [{'from': 'source', 'to': 'target'}], 'reading_order': [o['id'] for o in objects]}
    slide = deepcopy(source_slide)
    source_slide['notes_en'] = 'English public notes. Source and scope retained.'
    slide['notes_en'] = source_slide['notes_en']
    slide['exported_notes'] = slide['notes_en']
    slide['objects'][0]['resolved_link'] = title['link_target']
    slide['objects'][3]['route'] = {'fromSide': 'right', 'toSide': 'left', 'fromIdx': 3, 'toIdx': 1, 'start': [120, 225], 'end': [300, 225]}
    slide['objects'][4]['route'] = {'unconnected': True, 'start': [40, 350], 'end': [220, 350]}
    png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6TmcAAAAASUVORK5CYII=')
    slide['objects'][6]['media_sha256'] = native.digest(png)
    plan = {'schema_version': 'g6b3r1-export-plan-v1', 'model_sha256': '0' * 64,
            'manifest_sha256': '1' * 64, 'model': {'slides': [source_slide]}, 'slides': [slide]}

    def transform(obj):
        x, y, w, h = native.expected_box(obj)
        return f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'

    def line(obj, head=False):
        paint = obj.get('stroke', obj.get('color', '#000000'))[1:]
        return f'<a:ln w="{native.rounded(obj.get("stroke_width", 0) * native.EMU)}"><a:solidFill><a:srgbClr val="{paint}"/></a:solidFill>' + ('<a:tailEnd type="triangle"/>' if head else '') + '</a:ln>'

    def shape(obj, number):
        kind = 'line' if obj['kind'] in ('arrow', 'line') else 'rect' if obj['kind'] == 'text' else obj['kind']
        props = attrs({'id': number, 'name': obj['id'], 'descr': obj['alt']})
        fill = '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>' if kind in ('rect', 'ellipse') else '<a:noFill/>'
        body = ''
        if obj['kind'] == 'text':
            paragraphs = ''.join(f'<a:p><a:pPr algn="l"/><a:r><a:rPr sz="1800" b="1"><a:solidFill><a:srgbClr val="123456"/></a:solidFill><a:latin typeface="Nimbus Sans"/></a:rPr><a:t>{escape(text)}</a:t></a:r></a:p>' for text in obj['text'].split('\n'))
            body = '<p:txBody><a:bodyPr lIns="0" rIns="0" tIns="0" bIns="0" wrap="none"/><a:lstStyle/>' + paragraphs + '</p:txBody>'
        return f'<p:sp><p:nvSpPr><p:cNvPr {props}/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>{transform(obj)}<a:prstGeom prst="{kind}"><a:avLst/></a:prstGeom>{fill}{line(obj)}</p:spPr>{body}</p:sp>'

    connector = f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="90" name="tool-connector"/><p:cNvCxnSpPr><a:stCxn id="11" idx="3"/><a:endCxn id="12" idx="1"/></p:cNvCxnSpPr><p:nvPr/></p:nvCxnSpPr><p:spPr>{transform(arrow)}<a:prstGeom prst="line"><a:avLst/></a:prstGeom>{line(arrow, True)}</p:spPr></p:cxnSp>'
    image = f'<p:pic><p:nvPicPr><p:cNvPr id="91" name="tool-picture" descr="Native object"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="imageRel"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>{transform(picture)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
    namespaces = f'xmlns:p="{native.P}" xmlns:a="{native.A}" xmlns:r="{native.R}"'
    content = connector + image + ''.join(shape(obj, 10 + index) for index, obj in enumerate(objects) if obj['kind'] not in ('image',) and obj['id'] != 'arrow')
    slide_xml = f'<p:sld {namespaces}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>{content}</p:spTree></p:cSld></p:sld>'
    notes_text = ''.join(f'<a:p><a:r><a:t>{escape(text)}</a:t></a:r></a:p>' for text in slide['exported_notes'].split('\n'))
    notes = f'<p:notes {namespaces}><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="1" name="notes"/><p:cNvSpPr/><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr><p:txBody><a:bodyPr/><a:lstStyle/>{notes_text}</p:txBody></p:sp></p:spTree></p:cSld></p:notes>'
    rel = lambda text: f'<Relationships xmlns="{native.REL}">{text}</Relationships>'
    package = {
        'ppt/presentation.xml': f'<p:presentation {namespaces}><p:sldIdLst><p:sldId id="256" r:id="slideRel"/></p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/></p:presentation>'.encode(),
        'ppt/_rels/presentation.xml.rels': rel(f'<Relationship Id="slideRel" Type="{native.R}/slide" Target="slides/slide1.xml"/>').encode(),
        'ppt/slides/slide1.xml': slide_xml.encode(),
        'ppt/slides/_rels/slide1.xml.rels': rel(f'<Relationship Id="imageRel" Type="{native.R}/image" Target="../media/image.png"/><Relationship Id="notesRel" Type="{native.R}/notesSlide" Target="../notesSlides/notesSlide1.xml"/>').encode(),
        'ppt/notesSlides/notesSlide1.xml': notes.encode(), 'ppt/media/image.png': png,
    }
    return package, plan


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.raw, self.plan = fixture()
        self.package, self.changed = native.attach(self.raw, self.plan)

    def test_contain_fit_uses_authenticated_bitmap_dimensions(self):
        package, plan = fixture()
        for slide in (plan['slides'][0], plan['model']['slides'][0]):
            slide['objects'][6]['w'] = 120
        # A square original contained in a 120x100 allocation is centered at x=810.
        data = package['ppt/slides/slide1.xml']
        data = data.replace(b'<a:off x="7620000" y="2857500"/>', b'<a:off x="7715250" y="2857500"/>')
        data = data.replace(b'name="tool-picture" descr="Native object"', b'name="tool-picture"')
        package['ppt/slides/slide1.xml'] = data
        fixed, _ = native.attach(package, plan)
        native.inspect(fixed, plan)
        corrupted = dict(package)
        corrupted['ppt/slides/slide1.xml'] = data.replace(b'x="7715250"', b'x="7724775"')
        with self.assertRaises(ValueError):
            native.attach(corrupted, plan)
        corrupted = dict(package)
        corrupted['ppt/slides/slide1.xml'] = data.replace(b'name="tool-picture"', b'name="tool-picture" descr="Incorrect nonempty alt"')
        with self.assertRaises(ValueError):
            native.attach(corrupted, plan)
        corrupted = dict(package)
        corrupted['ppt/media/image.png'] += b'changed'
        with self.assertRaises(ValueError):
            native.attach(corrupted, plan)

    def test_zero_glyph_run_allowed_visible_unstyled_run_refused(self):
        root = native.xml(self.package['ppt/slides/slide1.xml'], 'test').documentElement
        _, objects = native.native_objects(root)
        title = objects[0]
        body = native.one(title, native.P, 'txBody')
        paragraph = native.children(body, native.A, 'p')[0]
        empty = native.add(paragraph, native.A, 'a:r')
        native.add(empty, native.A, 'a:t')
        native.check_style(title, self.plan['slides'][0]['objects'][0])
        run = native.children(paragraph, native.A, 'r')[0]
        run.removeChild(native.one(run, native.A, 'rPr'))
        with self.assertRaises(ValueError):
            native.check_style(title, self.plan['slides'][0]['objects'][0])

    def test_roundtrip_exact_native_contract(self):
        report = native.inspect(self.package, self.plan)
        self.assertEqual(report['slides'][0]['native_types'], {'sp': 5, 'cxnSp': 2, 'pic': 1})
        self.assertEqual(report['slides'][0]['hyperlinks'], 1)
        self.assertEqual(self.package['ppt/media/image.png'], self.raw['ppt/media/image.png'])

    def test_top_level_metadata_preserved_and_tamper_rejected(self):
        plan = deepcopy(self.plan)
        # A minimal synthetic package exercises preservation, not the 22-slide schema.
        fields = {'short_route': [f'S{index:02d}' for index in range(1, 12)],
                  'export_status': 'CONTENT_READY_FOR_WORK_EXPORT', 'runtime_authority': False}
        plan['model'].update(fields)
        package, changed = native.attach(self.raw, plan)
        self.assertIn('ppt/presentation.xml', changed)
        self.assertEqual(native.inspect(package, plan)['presentation_metadata'], fields)
        for before, after in [(b'S01', b'S22'), (b'CONTENT_READY_FOR_WORK_EXPORT', b'PASS'),
                              (b'false', b'true')]:
            with self.subTest(field=before):
                modified = dict(package)
                modified['ppt/presentation.xml'] = modified['ppt/presentation.xml'].replace(before, after, 1)
                with self.assertRaises(ValueError):
                    native.inspect(modified, plan)

    def test_signed_line_and_arrow_geometry(self):
        plan = deepcopy(self.plan)
        for slide in (plan['slides'][0], plan['model']['slides'][0]):
            slide['objects'][3].update(x=300, w=-180, source_id='target', target_id='source')
            slide['objects'][4].update(x=220, w=-180)
            slide['objects'][5].update(y=300, h=-200)
        plan['slides'][0]['objects'][3]['route'] = {
            'fromSide': 'left', 'toSide': 'right', 'fromIdx': 1, 'toIdx': 3,
            'start': [300, 225], 'end': [120, 225]}
        plan['slides'][0]['objects'][4]['route'] = {'unconnected': True, 'start': [220, 350], 'end': [40, 350]}
        raw = dict(self.raw)
        document = native.xml(raw['ppt/slides/slide1.xml'], 'slide')
        connector = native.descend(document, native.P, 'cxnSp')[0]
        start, end = native.connector_endpoints(connector)
        start.setAttribute('id', '12'); start.setAttribute('idx', '1')
        end.setAttribute('id', '11'); end.setAttribute('idx', '3')
        raw['ppt/slides/slide1.xml'] = native.serialize(document)
        package, _ = native.attach(raw, plan)
        native.inspect(package, plan)
        root = native.xml(package['ppt/slides/slide1.xml'], 'slide').documentElement
        _, objects = native.native_objects(root)
        for index, flip in [(3, 'flipH'), (4, 'flipH'), (5, 'flipV')]:
            transform = native.chain(objects[index], (native.P, 'spPr'), (native.A, 'xfrm'))
            self.assertEqual(transform.getAttribute(flip), '1')
            self.assertTrue(all(value >= 0 for value in native.box(objects[index])))

    def test_mutations_rejected(self):
        for before, after in [
            (b'<a:tailEnd type="triangle"', b'<a:tailEnd type="none"'),
            (b'sz="1800"', b'sz="1700"'),
            (b'Title</a:t>', b'Wrong</a:t>'),
            (b'Exact second line</a:t>', b'Lost newline</a:t>'),
            (b'anchor="t"', b'anchor="ctr"'),
            (b'val="2250"', b'val="2000"'),
            (b'name="title"', b'name="unstable"'),
            (b'cx="0"', b'cx="10"'),
            (b'typeface="Nimbus Sans"', b'typeface="Helvetica"'),
            (b'<a:stCxn id="3"', b'<a:stCxn id="2"'),
            (b'relation_type', b'broken_metadata'),
        ]:
            with self.subTest(before=before):
                changed = dict(self.package)
                self.assertIn(before, changed['ppt/slides/slide1.xml'])
                changed['ppt/slides/slide1.xml'] = changed['ppt/slides/slide1.xml'].replace(before, after, 1)
                with self.assertRaises(ValueError):
                    native.inspect(changed, self.plan)

    def test_tampered_notes_image_and_links(self):
        for part in ('ppt/notesSlides/notesSlide1.xml', 'ppt/media/image.png', 'ppt/slides/_rels/slide1.xml.rels'):
            with self.subTest(part=part):
                changed = dict(self.package)
                if 'notes' in part:
                    self.assertIn(b'English public notes', changed[part])
                    changed[part] = changed[part].replace(b'English public notes', b'Wrong public notes', 1)
                elif 'media' in part:
                    changed[part] += b'tamper'
                else:
                    changed[part] = changed[part].replace(b'/blob/main/', b'/blob/wrong/', 1)
                self.assertNotEqual(changed[part], self.package[part])
                with self.assertRaises(ValueError):
                    native.inspect(changed, self.plan)

    def test_canonical_zip_repeatability(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix='.unit-') as directory:
            first, second = Path(directory) / 'first.zip', Path(directory) / 'second.zip'
            native.write_package(first, self.package); native.write_package(second, self.package)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            native.inspect(native.load_package(first), self.plan)

    def test_multiline_alt_survives_xml_attribute_normalization(self):
        plan = deepcopy(self.plan)
        for slide in (plan['slides'][0], plan['model']['slides'][0]):
            slide['objects'][0]['alt'] = 'First line\nSecond line\twith tab'
        package, _ = native.attach(self.raw, plan)
        native.inspect(package, plan)
        self.assertIn(b'First line&#10;Second line&#9;with tab', package['ppt/slides/slide1.xml'])

    def test_offline_hyperlink_ooxml_cli_and_manifest_binding(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix='.unit-') as directory:
            root = Path(directory) / 'handoff'
            (root / 'presentation').mkdir(parents=True)
            (root / 'sources').mkdir()
            target = root / 'sources/Claim notes.html'
            content = b'<h1 id="scope">Offline source</h1>'
            target.write_bytes(content)
            plan = deepcopy(self.plan)
            original = '../sources/Claim notes.html#scope'
            uri = '../sources/Claim%20notes.html#scope'
            for slide in (plan['slides'][0], plan['model']['slides'][0]):
                slide['objects'][0]['link_target'] = original
                slide['source_refs'] = [{'label': 'Source', 'target': original}]
            slide = plan['slides'][0]
            slide['objects'][0]['resolved_link'] = uri
            slide['resolved_refs'] = [{'label': 'Source', 'target': original, 'url': uri}]
            slide['exported_notes'] += '\nSource: ' + original + '\n[' + uri + ']'
            model_bytes = json.dumps(plan['model'], ensure_ascii=False).encode()
            (root / 'presentation/main_native_objects.json').write_bytes(model_bytes)
            plan.update(model_path='presentation/main_native_objects.json', manifest_path='SOURCE_MANIFEST.json',
                        final_pptx_path='presentation/main.pptx', model_sha256=native.digest(model_bytes),
                        local_links=[{'uri': uri, 'source_path': 'sources/Claim notes.html',
                                      'bytes': len(content), 'sha256': native.digest(content)}])
            manifest = {'schema_version': 'g6b3r1-source-manifest-v1', 'files': [
                {'path': plan['model_path'], 'bytes': len(model_bytes), 'sha256': native.digest(model_bytes)},
                {'path': 'sources/Claim notes.html', 'bytes': len(content), 'sha256': native.digest(content)}]}
            manifest_bytes = json.dumps(manifest).encode()
            (root / 'SOURCE_MANIFEST.json').write_bytes(manifest_bytes)
            plan['manifest_sha256'] = native.digest(manifest_bytes)
            self.assertEqual(native.verify_local_sources(plan, root)['local_links_verified'], 1)

            raw = dict(self.raw)
            notes = native.xml(raw['ppt/notesSlides/notesSlide1.xml'], 'notes')
            body = native.notes_body(notes)
            for paragraph in native.children(body, native.A, 'p'):
                body.removeChild(paragraph)
            for text in slide['exported_notes'].split('\n'):
                paragraph = native.add(body, native.A, 'a:p')
                run = native.add(paragraph, native.A, 'a:r')
                node = native.add(run, native.A, 'a:t')
                node.appendChild(notes.createTextNode(text))
            raw['ppt/notesSlides/notesSlide1.xml'] = native.serialize(notes)
            candidate = root / 'synthetic-input.zip'
            native.write_package(candidate, raw)
            plan_file = root / 'synthetic-plan.json'
            plan_file.write_text(json.dumps(plan, ensure_ascii=False))
            output = root / 'presentation/synthetic-native.zip'
            command = [sys.executable, str(Path(native.__file__).resolve()), 'attach', '--plan', str(plan_file),
                       '--presentation-root', str(root), '--input', str(candidate), '--output', str(output),
                       '--report', str(root / 'synthetic-report.json')]
            subprocess.run(command, check=True, capture_output=True, text=True)
            package = native.load_package(output)
            native.inspect(package, plan)
            _, relations = native.relationships(package, 'ppt/slides/slide1.xml')
            link = relations['g6b3r1Link1']
            self.assertEqual(link.getAttribute('Target'), uri)
            self.assertEqual(link.getAttribute('TargetMode'), 'External')
            self.assertIn(original, native.text_content(native.notes_body(native.xml(package['ppt/notesSlides/notesSlide1.xml'], 'notes'))))

            relocated = Path(directory) / 'relocated-bundle'
            shutil.copytree(root, relocated)
            self.assertEqual(native.verify_local_sources(plan, root), native.verify_local_sources(plan, relocated))
            broken = deepcopy(plan); broken['local_links'] = []
            with self.assertRaises(ValueError):
                native.inspect(package, broken)
            target.write_bytes(content + b'tamper')
            with self.assertRaises(ValueError):
                native.verify_local_sources(plan, root)
            target.unlink()
            target.symlink_to(relocated / 'sources/Claim notes.html')
            with self.assertRaises(ValueError):
                native.verify_local_sources(plan, root)

    def test_offline_uri_parser(self):
        self.assertEqual(native.local_link('../sources/Claim%20notes.html#page=2', 'presentation/model.json'),
                         {'uri': '../sources/Claim%20notes.html#page=2', 'source_path': 'sources/Claim notes.html'})
        for target in ('../../escape', '../%2e%2e/escape', '%252e%252e/escape', '../source%2ffile',
                       '//server/share', '/absolute', 'file:///tmp/file', '../bad%ZZ', '#no-file', '../a?query=1'):
            with self.subTest(target=target), self.assertRaises(ValueError):
                native.local_link(target, 'presentation/model.json')

    def test_no_double_attachment_or_unsafe_xml(self):
        with self.assertRaises(ValueError):
            native.attach(self.package, self.plan)
        with self.assertRaises(ValueError):
            native.xml(b'<!DOCTYPE s [<!ENTITY x "bad">]><s>&x;</s>', 'test.xml')
        with self.assertRaises(ValueError):
            native.strict_json('{"a":1,"a":2}')


if __name__ == '__main__':
    unittest.main()
