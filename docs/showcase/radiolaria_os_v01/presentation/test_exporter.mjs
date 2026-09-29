import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {validateSchema, checkModel, arrowRoute, objectBox, relativeName, githubURL, parseJSON, localLink, prepare} from './build_main.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const schema = parseJSON(await fs.readFile(path.join(here, 'main_native_objects.schema.json')));
const base = {x: 0, y: 0, w: 100, h: 40, alt: 'Native object', reading_order: 0};
const title = {...base, id: 'title', kind: 'text', text: 'Title\nExact second line', font_px: 24,
  color: '#123456', bold: true, line_height_px: 30, entity_id: 'claim-title', link_target: '../sources/claim.md#anchor'};
const a = {...base, id: 'source', kind: 'rect', x: 20, y: 200, h: 50, reading_order: 1,
  fill: '#FFFFFF', stroke: '#123456', stroke_width: 1};
const b = {...a, id: 'target', x: 300, reading_order: 2};
const arrow = {...base, id: 'attached', kind: 'arrow', x: 120, y: 225, w: 180, h: 0,
  reading_order: 3, source_id: 'source', target_id: 'target', head: 'triangle', color: '#123456', stroke_width: 2,
  relation_type: 'comparison'};
const free = {...arrow, id: 'free', x: 50, y: 300, reading_order: 4, source_id: null, target_id: null};
const vertical = {...base, id: 'vertical', kind: 'line', x: 500, y: 100, w: 0, h: 150,
  reading_order: 5, color: '#123456', stroke_width: 1};
const picture = {...base, id: 'image', kind: 'image', x: 800, y: 300, w: 100, h: 100,
  reading_order: 6, path: '../assets/pixel.png', originalbitmap: true};
const slide = {id: 's01', title: title.text, notes_ru: '\u0420\u0443\u0441\u0441\u043a\u0438\u0435 \u0437\u0430\u043c\u0435\u0442\u043a\u0438.',
  notes_en: 'English public notes. Exact source boundary.',
  source_refs: [{label: 'Source', target: '../sources/claim.md#anchor'}],
  scope: {claim: 'bounded', number: 1}, relations: [{from: 'source', to: 'target', kind: 'comparison'}],
  objects: [title, a, b, arrow, free, vertical, picture]};
slide.reading_order = slide.objects.map(object => object.id);
const model = {schema_version: 'g6b3r1-native-v1', canvas: {width: 1280, height: 720, unit: 'css_px', dpi: 96}, font: 'Nimbus Sans',
  short_route: Array.from({length: 14}, (_, index) => `s${index + 1}`),
  export_status: 'CONTENT_READY_FOR_WORK_EXPORT', runtime_authority: false,
  slides: Array.from({length: 25}, (_, index) => ({...structuredClone(slide), id: `s${index + 1}`}))};
validateSchema(model, schema); checkModel(model);
const wrappedTitle = structuredClone(model);
wrappedTitle.slides[0].title = 'Title Exact second line';
checkModel(wrappedTitle);
assert.ok(slide.notes_en.includes('English'));
const bad = mutate => { const clone = structuredClone(model); mutate(clone); assert.throws(() => { validateSchema(clone, schema); checkModel(clone); }); };
bad(value => { value.slides.pop(); });
bad(value => { delete value.slides[0].notes_en; });
bad(value => { value.slides[0].notes_en = ''; });
bad(value => { value.font = 'Helvetica'; });
bad(value => { value.slides[0].objects[0].fontSizePt = 18; });
bad(value => { value.slides[0].objects[0].kind = 'svg'; });
bad(value => { value.slides[0].objects[0].line_height_px = 0; });
bad(value => { value.slides[0].objects[4].target_id = 'target'; });
bad(value => { value.slides[0].objects[3].w += 1; });
bad(value => { value.slides[0].objects[5].h = 0; });
bad(value => { value.slides[0].objects[2].reading_order = 0; });
bad(value => { value.slides[0].title = 'Dropped title'; });
bad(value => { value.slides[0].objects[6].originalbitmap = false; });
bad(value => { value.slides[0].scope_unknown = 'not permitted'; });
bad(value => { value.short_route.pop(); });
bad(value => { value.short_route[0] = value.short_route[1]; });
bad(value => { value.short_route[0] = 'missing-slide'; });
bad(value => { value.export_status = 'PASS'; });
bad(value => { value.runtime_authority = true; });
const objects = new Map([a, b].map(object => [object.id, object]));
assert.equal(arrowRoute(arrow, objects).fromSide, 'right');
assert.equal(arrowRoute({...arrow, source_id: 'target', target_id: 'source'}, objects).fromSide, 'left');
const leftward = {...arrow, x: 300, w: -180, source_id: 'target', target_id: 'source'};
assert.deepEqual(objectBox(leftward), [120, 225, 180, 0]);
assert.deepEqual(arrowRoute(leftward, objects), {fromSide: 'left', toSide: 'right', start: [300, 225], end: [120, 225]});
assert.equal(arrowRoute({...leftward, x: 350, y: 250, w: -280, h: -50}, objects).fromSide, 'bottom');
const signed = structuredClone(model);
signed.slides[0].objects[3] = leftward;
signed.slides[0].objects[4] = {...free, x: 400, w: -180};
signed.slides[0].objects[5] = {...vertical, y: 250, h: -150};
validateSchema(signed, schema); checkModel(signed);
bad(value => { value.slides[0].objects[5].h = -151; });
assert.equal(arrowRoute(free, objects).unconnected, true);
assert.throws(() => relativeName('../escape.png'));
assert.throws(() => githubURL('file:///private/tmp/source'));
assert.throws(() => githubURL('https://github.com.evil.invalid/o/r/blob/main/file'));
assert.deepEqual(localLink('../sources/Claim%20notes.html#page=2', 'presentation/main_native_objects.json'),
  {uri: '../sources/Claim%20notes.html#page=2', source_path: 'sources/Claim notes.html'});
assert.deepEqual(localLink('./reader.html#part%20one', 'presentation/main_native_objects.json'),
  {uri: 'reader.html#part%20one', source_path: 'presentation/reader.html'});
for (const target of ['../../escape.md', '../%2e%2e/escape.md', '%252e%252e/escape.md',
  '../sources%2fclaim.md', '//host/share', '/absolute/file', 'file:///local/file',
  'C:\\local\\file', '../bad%ZZ.md', '#no-file', '../sources/claim.md?query=1', '../sources/claim.md#bad%0a']) {
  assert.throws(() => localLink(target, 'presentation/main_native_objects.json'), target);
}
assert.throws(() => parseJSON('{"x":1,"x":2}'));
assert.throws(() => parseJSON('{"x":1,"\\u0078":2}'));
assert.throws(() => parseJSON('{"x":1e999}'));
assert.deepEqual(parseJSON('{"a":[{"b":"quotes \\\" retained"}, null]}'), {a: [{b: 'quotes " retained'}, null]});

const temporary = await fs.mkdtemp(path.join(here, '.unit-'));
try {
  await fs.mkdir(path.join(temporary, 'presentation'));
  await fs.mkdir(path.join(temporary, 'assets'));
  await fs.mkdir(path.join(temporary, 'sources'));
  const modelName = path.relative(here, path.join(temporary, 'presentation/main_native_objects.json'));
  const mapName = path.relative(here, path.join(temporary, 'link_map.json'));
  const manifestName = path.relative(here, path.join(temporary, 'SOURCE_MANIFEST.json'));
  await fs.writeFile(path.join(here, modelName), JSON.stringify(wrappedTitle));
  await fs.writeFile(path.join(here, mapName), JSON.stringify({schema_version: 'g6b3r1-link-map-v1', links: [
    {target: 'reader-entry', url: '../sources/claim.md#anchor'}]}));
  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6TmcAAAAASUVORK5CYII=', 'base64');
  const assetName = path.relative(here, path.join(temporary, 'assets/pixel.png'));
  await fs.writeFile(path.join(here, assetName), png);
  const sourceName = path.relative(here, path.join(temporary, 'sources/claim.md'));
  const sourceBytes = Buffer.from('# Source\n<a id="anchor"></a>\nBound offline source.\n');
  await fs.writeFile(path.join(here, sourceName), sourceBytes);
  const writeManifest = async () => {
    const files = [];
    for (const file of ['build_main.mjs', 'attach_links.py', 'main_native_objects.schema.json', 'source_manifest.schema.json',
      'link_map.schema.json', modelName, mapName, assetName, sourceName]) {
      const data = await fs.readFile(path.join(here, file));
      files.push({path: file, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')});
    }
    await fs.writeFile(path.join(here, manifestName), JSON.stringify({schema_version: 'g6b3r1-source-manifest-v1', files}));
  };
  await writeManifest();
  const args = [path.join(here, 'build_main.mjs'), 'validate', '--presentation-root', here,
    '--model', modelName, '--manifest', manifestName];
  const options = {'presentation-root': here, model: modelName, manifest: manifestName};
  const result = JSON.parse(execFileSync(process.execPath, args, {encoding: 'utf8'}));
  assert.equal(result.slides, 25);
  assert.equal(result.status, 'SOURCE_VALIDATED_ONLY_NO_EXPORT');
  assert.equal(result.local_links_verified, 1);
  assert.equal(result.final_pptx_path, path.posix.join(path.posix.dirname(modelName), 'main.pptx'));
  const context = await prepare(options);
  assert.deepEqual(context.plan.model.short_route, model.short_route);
  assert.equal(context.plan.model.export_status, 'CONTENT_READY_FOR_WORK_EXPORT');
  assert.equal(context.plan.model.runtime_authority, false);
  assert.equal(context.plan.slides[0].objects[0].resolved_link, '../sources/claim.md#anchor');
  assert.equal(context.plan.slides[0].objects[0].text, title.text);
  assert.ok(context.plan.slides[0].exported_notes.startsWith(slide.notes_en));
  assert.ok(!context.plan.slides[0].exported_notes.includes(slide.notes_ru));
  assert.equal(context.plan.slides[0].title, 'Title Exact second line');
  assert.ok(context.plan.slides[0].exported_notes.includes('Source: ../sources/claim.md#anchor'));
  assert.equal(context.plan.local_links[0].source_path, sourceName);
  assert.equal(context.plan.local_links[0].sha256, createHash('sha256').update(sourceBytes).digest('hex'));

  const aliases = structuredClone(wrappedTitle);
  for (const item of aliases.slides) { item.source_refs[0].target = 'reader-entry'; item.objects[0].link_target = 'reader-entry'; }
  await fs.writeFile(path.join(here, modelName), JSON.stringify(aliases)); await writeManifest();
  const mapped = await prepare({...options, 'link-map': mapName});
  assert.equal(mapped.plan.slides[0].objects[0].resolved_link, '../sources/claim.md#anchor');
  assert.ok(mapped.plan.slides[0].exported_notes.includes('Source: reader-entry\n[../sources/claim.md#anchor]'));

  const unbound = structuredClone(wrappedTitle);
  unbound.slides[0].source_refs[0].target = '../sources/unlisted.md';
  await fs.writeFile(path.join(temporary, 'sources/unlisted.md'), 'Not in manifest');
  await fs.writeFile(path.join(here, modelName), JSON.stringify(unbound)); await writeManifest();
  await assert.rejects(prepare(options), /Consumed input missing from SOURCE_MANIFEST/u);

  await fs.writeFile(path.join(here, modelName), JSON.stringify(wrappedTitle)); await writeManifest();
  await fs.appendFile(path.join(here, sourceName), 'tamper');
  await assert.rejects(prepare(options), /SOURCE_MANIFEST mismatch/u);
  await fs.writeFile(path.join(here, sourceName), sourceBytes);
  await fs.unlink(path.join(here, sourceName));
  await fs.symlink(path.join(temporary, 'sources/unlisted.md'), path.join(here, sourceName));
  await assert.rejects(prepare(options), /Symlink source forbidden/u);
  await fs.unlink(path.join(here, sourceName));
  await fs.mkdir(path.join(here, sourceName));
  await assert.rejects(prepare(options), /Not a regular file/u);
  await fs.rmdir(path.join(here, sourceName));
  await assert.rejects(prepare(options), /ENOENT/u);
  await fs.writeFile(path.join(here, sourceName), sourceBytes);
  await fs.appendFile(path.join(here, assetName), 'tamper');
  assert.throws(() => execFileSync(process.execPath, args, {encoding: 'utf8', stdio: 'pipe'}), /SOURCE_MANIFEST mismatch/u);
} finally {
  await fs.rm(temporary, {recursive: true, force: true});
}
console.log('Source-only tests succeeded: 25 slides, 14 short-route IDs, English notes, wrapped title, offline links without a map, optional local aliases, URI fragments, manifest bytes, traversal/symlink/nonfile/tamper rejection. No export executed.');
