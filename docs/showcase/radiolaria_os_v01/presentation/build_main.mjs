#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath, pathToFileURL} from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CODE = ['build_main.mjs', 'attach_links.py', 'main_native_objects.schema.json',
  'source_manifest.schema.json', 'link_map.schema.json'];
const EMU = 9525;
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const fail = message => { throw new Error(message); };
const check = (condition, message) => { if (!condition) fail(message); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const titleMatches = (text, title) => text.replace(/\s+/gu, ' ').trim() === title.replace(/\s+/gu, ' ').trim();

export function parseJSON(bytes) {
  const source = String(bytes), result = JSON.parse(source);
  let offset = 0;
  const whitespace = () => { while (/\s/u.test(source[offset] ?? '') && offset < source.length) offset++; };
  const string = () => {
    const start = offset++;
    while (source[offset] !== '"') { if (source[offset] === '\\') offset++; offset++; }
    return JSON.parse(source.slice(start, ++offset));
  };
  const value = () => {
    whitespace(); const token = source[offset];
    if (token === '{') {
      offset++; whitespace(); const keys = new Set();
      if (source[offset] !== '}') while (true) {
        whitespace(); const key = string();
        check(!keys.has(key), `Duplicate JSON key: ${key}`); keys.add(key);
        whitespace(); offset++; value(); whitespace();
        if (source[offset] !== ',') break;
        offset++;
      }
      offset++;
    } else if (token === '[') {
      offset++; whitespace();
      if (source[offset] !== ']') while (true) {
        value(); whitespace(); if (source[offset] !== ',') break; offset++;
      }
      offset++;
    } else if (token === '"') string();
    else while (offset < source.length && !/[\s,}\]]/u.test(source[offset])) offset++;
  };
  value();
  const finiteJSON = item => {
    if (typeof item === 'number') check(Number.isFinite(item), 'Nonfinite JSON number');
    else if (item && typeof item === 'object') Object.values(item).forEach(finiteJSON);
  };
  finiteJSON(result); return result;
}

// This interpreter implements exactly the keywords used in the three shipped schemas.
export function validateSchema(value, schema, root = schema, where = '$') {
  const supported = new Set(['$schema', '$id', 'title', '$defs', '$ref', 'type', 'const',
    'enum', 'required', 'properties', 'additionalProperties', 'items', 'minItems', 'maxItems',
    'minLength', 'pattern', 'minimum', 'exclusiveMinimum', 'oneOf']);
  for (const key of Object.keys(schema)) check(supported.has(key), `Unknown schema keyword: ${key}`);
  if (schema.$ref) {
    check(schema.$ref.startsWith('#/$defs/'), `Nonlocal schema reference: ${schema.$ref}`);
    const target = root.$defs[schema.$ref.slice(8)];
    check(target, `Missing schema definition: ${schema.$ref}`);
    return validateSchema(value, target, root, where);
  }
  if (schema.oneOf) {
    const errors = [];
    const matches = schema.oneOf.filter(branch => {
      try { validateSchema(value, branch, root, where); return true; }
      catch (error) { errors.push(error.message); return false; }
    });
    check(matches.length === 1, `${where}: expected exactly one supported object kind; ${errors.join('; ')}`);
  }
  if ('const' in schema) check(same(value, schema.const), `${where}: expected ${JSON.stringify(schema.const)}`);
  if (schema.enum) check(schema.enum.some(item => same(item, value)), `${where}: unsupported value`);
  if (schema.type) {
    const valid = schema.type === 'array' ? Array.isArray(value)
      : schema.type === 'object' ? value !== null && typeof value === 'object' && !Array.isArray(value)
      : schema.type === 'integer' ? Number.isSafeInteger(value)
      : schema.type === 'number' ? typeof value === 'number' && Number.isFinite(value)
      : typeof value === schema.type;
    check(valid, `${where}: expected ${schema.type}`);
  }
  if (typeof value === 'number') {
    if ('minimum' in schema) check(value >= schema.minimum, `${where}: below minimum`);
    if ('exclusiveMinimum' in schema) check(value > schema.exclusiveMinimum, `${where}: must be positive`);
  }
  if (typeof value === 'string') {
    if (schema.minLength) check([...value].length >= schema.minLength, `${where}: empty string`);
    if (schema.pattern) check(new RegExp(schema.pattern, 'u').test(value), `${where}: invalid format`);
    check(!/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ud800-\udfff\ufffe\uffff]/u.test(value), `${where}: invalid XML character`);
    check(!value.includes('\r'), `${where}: use LF line endings, not CR`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems) check(value.length >= schema.minItems, `${where}: too few items`);
    if (schema.maxItems) check(value.length <= schema.maxItems, `${where}: too many items`);
    if (schema.items) value.forEach((item, index) => validateSchema(item, schema.items, root, `${where}[${index}]`));
  } else if (value !== null && typeof value === 'object') {
    for (const key of schema.required ?? []) check(Object.hasOwn(value, key), `${where}: missing ${key}`);
    for (const [key, item] of Object.entries(value)) {
      const property = schema.properties?.[key];
      if (property) validateSchema(item, property, root, `${where}.${key}`);
      else check(schema.additionalProperties !== false, `${where}: unsupported field ${key}`);
    }
  }
}

export function relativeName(value) {
  check(typeof value === 'string' && value.length > 0 && !/[\\\u0000-\u001f:?#]/u.test(value), `Unsafe relative path: ${value}`);
  check(!path.posix.isAbsolute(value) && value.split('/').every(x => x && x !== '.' && x !== '..'), `Noncanonical relative path: ${value}`);
  return value;
}

function under(root, filename) {
  const relative = path.relative(root, filename);
  check(relative && relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative), `Path outside presentation root: ${filename}`);
  return relative.split(path.sep).join('/');
}

async function inputFile(root, relative) {
  relativeName(relative);
  let current = root;
  for (const component of relative.split('/')) {
    current = path.join(current, component);
    check(!(await fs.lstat(current)).isSymbolicLink(), `Symlink source forbidden: ${relative}`);
  }
  check((await fs.stat(current)).isFile(), `Not a regular file: ${relative}`);
  under(root, await fs.realpath(current));
  return current;
}

export function githubURL(value) {
  let url;
  try { url = new URL(value); } catch { fail(`Expected resolved GitHub HTTPS URL: ${value}`); }
  check(url.protocol === 'https:' && url.hostname === 'github.com' && !url.port && !url.username && !url.password,
    `Remote links must be explicit source GitHub HTTPS URLs: ${value}`);
  check(/^\/[^/]+\/[^/]+\/(blob|tree|commit|issues|pull|releases)\/.+/u.test(url.pathname), `Expected a specific GitHub source target: ${value}`);
  check(!/[\s\u0000-\u001f]/u.test(value), `URL must be percent encoded: ${value}`);
  return value;
}

function uriSegment(value) {
  return encodeURIComponent(value).replace(/[!'()*]/gu, character => `%${character.charCodeAt(0).toString(16).toUpperCase()}`);
}

export function localLink(value, modelName) {
  relativeName(modelName);
  check(typeof value === 'string' && value.length > 0, 'Local hyperlink must be a nonempty string');
  const hash = value.indexOf('#');
  const rawPath = hash < 0 ? value : value.slice(0, hash);
  const rawFragment = hash < 0 ? null : value.slice(hash + 1);
  check(rawPath && !rawPath.startsWith('/') && !/[\\\u0000-\u001f\u007f:?]/u.test(rawPath), `Invalid relative file hyperlink: ${value}`);
  check(!/%(?:2f|5c)/iu.test(rawPath), `Encoded path separators are forbidden: ${value}`);
  let decoded, fragment;
  try { decoded = decodeURIComponent(rawPath); fragment = rawFragment === null ? null : decodeURIComponent(rawFragment); }
  catch { fail(`Malformed URI encoding: ${value}`); }
  check(!decoded.startsWith('/') && !/[\\\u0000-\u001f\u007f:?#]/u.test(decoded)
    && !/%[0-9a-f]{2}/iu.test(decoded), `Unsafe or multiply encoded local hyperlink: ${value}`);
  check(fragment === null || !/[\u0000-\u001f\u007f]/u.test(fragment), `Invalid hyperlink fragment: ${value}`);
  const directory = path.posix.dirname(modelName);
  const components = directory === '.' ? [] : directory.split('/');
  for (const component of decoded.split('/')) {
    check(component.length > 0, `Empty local path component: ${value}`);
    if (component === '.') continue;
    if (component === '..') {
      check(components.length > 0, `Local hyperlink traverses outside handoff: ${value}`);
      components.pop();
    } else components.push(component);
  }
  const source_path = relativeName(components.join('/'));
  const relative = path.posix.relative(directory, source_path);
  check(relative.length > 0, `Hyperlink must target a file, not the presentation directory: ${value}`);
  const encodedPath = relative.split('/').map(uriSegment).join('/');
  // Preserve fragment delimiters used by HTML anchors and PDF page= navigation.
  const encodedFragment = fragment === null ? '' : '#' + encodeURI(fragment).replace(/#/gu, '%23');
  return {uri: encodedPath + encodedFragment, source_path};
}

function anchors(object) {
  return [
    ['right', object.x + object.w, object.y + object.h / 2],
    ['left', object.x, object.y + object.h / 2],
    ['bottom', object.x + object.w / 2, object.y + object.h],
    ['top', object.x + object.w / 2, object.y],
  ];
}

export function objectBox(object) {
  return ['line', 'arrow'].includes(object.kind)
    ? [Math.min(object.x, object.x + object.w), Math.min(object.y, object.y + object.h), Math.abs(object.w), Math.abs(object.h)]
    : [object.x, object.y, object.w, object.h];
}

export function arrowRoute(object, objects) {
  if (object.source_id === null && object.target_id === null) return {
    unconnected: true, start: [object.x, object.y], end: [object.x + object.w, object.y + object.h]};
  check(typeof object.source_id === 'string' && typeof object.target_id === 'string', `${object.id}: both arrow endpoints must be strings or both null`);
  const source = objects.get(object.source_id), target = objects.get(object.target_id);
  check(source && target && source !== target, `${object.id}: missing or self-referential arrow endpoints`);
  for (const endpoint of [source, target]) check(['text', 'rect', 'ellipse'].includes(endpoint.kind), `${object.id}: endpoint must be text, rect or ellipse`);
  const candidates = [];
  for (const [fromSide, sx, sy] of anchors(source)) {
    for (const [toSide, tx, ty] of anchors(target)) {
      const signed = object.w < 0 || object.h < 0;
      const actual = signed ? [sx, sy, tx - sx, ty - sy]
        : [Math.min(sx, tx), Math.min(sy, ty), Math.abs(tx - sx), Math.abs(ty - sy)];
      if (actual.every((value, index) => Math.abs(value - [object.x, object.y, object.w, object.h][index]) <= 1 / EMU)) {
        candidates.push({fromSide, toSide, start: [sx, sy], end: [tx, ty]});
      }
    }
  }
  check(candidates.length === 1, `${object.id}: box/signed deltas must identify one straight native midpoint-anchor route; found ${candidates.length}`);
  return candidates[0];
}

export function checkModel(model) {
  const slides = new Set(); let slideOrder = -1;
  for (const slide of model.slides) {
    check(!slides.has(slide.id), `Duplicate slide id: ${slide.id}`); slides.add(slide.id);
    const objects = new Map(); let prior = -1;
    if (typeof slide.reading_order === 'number') {
      check(slide.reading_order > slideOrder, `${slide.id}: slide reading_order must increase in input order`);
      slideOrder = slide.reading_order;
    } else if (Array.isArray(slide.reading_order)) {
      check(same(slide.reading_order, slide.objects.map(object => object.id)), `${slide.id}: slide reading_order must match object input order`);
    }
    for (const object of slide.objects) {
      check(!objects.has(object.id), `${slide.id}: duplicate object id ${object.id}`);
      objects.set(object.id, object);
      check(object.reading_order > prior, `${slide.id}: reading_order must strictly increase in input order`);
      prior = object.reading_order;
      const [x, y, w, h] = objectBox(object);
      check(x >= 0 && y >= 0 && x + w <= model.canvas.width && y + h <= model.canvas.height, `${object.id}: off-canvas geometry`);
      if (['line', 'arrow'].includes(object.kind)) check(object.w !== 0 || object.h !== 0, `${object.id}: point is not a line`);
      if (object.kind === 'image') {
        check(!path.posix.isAbsolute(object.path) && !/[\\\u0000-\u001f:?#]/u.test(object.path), `${object.id}: image path must be local and relative to the model directory`);
        check(!(object.x === 0 && object.y === 0 && object.w === 1280 && object.h === 720), `${object.id}: full-slide bitmap forbidden`);
      }
      if (object.kind === 'text') check(object.font_px * 75 >= 100 && object.font_px * 75 <= 400000, `${object.id}: font size outside OOXML range`);
      if (['rect', 'ellipse'].includes(object.kind)) check((object.stroke === 'none') === (object.stroke_width === 0), `${object.id}: no stroke means zero width; colored stroke needs positive width`);
    }
    check(slide.objects.some(o => o.kind === 'text' && titleMatches(o.text, slide.title)), `${slide.id}: title must occur in native text, permitting explicit line wrapping only`);
    for (const object of slide.objects) if (object.kind === 'arrow') arrowRoute(object, objects);
  }
  if (model.short_route) {
    check(new Set(model.short_route).size === model.short_route.length, 'short_route must contain unique stable slide IDs');
    for (const id of model.short_route) check(slides.has(id), `short_route references an absent slide: ${id}`);
  }
}

export async function prepare(options) {
  const root = await fs.realpath(path.resolve(options['presentation-root']));
  const manifestName = options.manifest ?? 'SOURCE_MANIFEST.json';
  const manifestBytes = await fs.readFile(await inputFile(root, manifestName));
  const schemas = Object.fromEntries(await Promise.all(['source_manifest', 'main_native_objects', 'link_map'].map(async name =>
    [name, parseJSON(await fs.readFile(path.join(HERE, `${name}.schema.json`), 'utf8'))])));
  const manifest = parseJSON(manifestBytes);
  validateSchema(manifest, schemas.source_manifest);
  if (options['manifest-sha256']) check(sha(manifestBytes) === options['manifest-sha256'], 'SOURCE_MANIFEST hash differs from supplied pin');
  const rows = new Map(), folded = new Set();
  for (const row of manifest.files) {
    relativeName(row.path);
    check(row.path !== manifestName && !folded.has(row.path.toLowerCase()), `Self-entry or path collision: ${row.path}`);
    folded.add(row.path.toLowerCase()); rows.set(row.path, row);
    const bytes = await fs.readFile(await inputFile(root, row.path));
    check(bytes.length === row.bytes && sha(bytes) === row.sha256, `SOURCE_MANIFEST mismatch: ${row.path}`);
  }
  const read = async relative => {
    const row = rows.get(relative); check(row, `Consumed input missing from SOURCE_MANIFEST: ${relative}`);
    const bytes = await fs.readFile(await inputFile(root, relative));
    check(bytes.length === row.bytes && sha(bytes) === row.sha256, `Source changed while reading: ${relative}`);
    return bytes;
  };
  for (const file of CODE) await read(under(root, path.join(HERE, file)));
  const modelName = options.model ?? 'main_native_objects.json';
  const modelBytes = await read(modelName), model = parseJSON(modelBytes);
  validateSchema(model, schemas.main_native_objects); checkModel(model);
  const mapping = new Map(), used = new Set();
  if (options['link-map']) {
    const map = parseJSON(await read(options['link-map'])); validateSchema(map, schemas.link_map);
    for (const item of map.links) {
      check(!mapping.has(item.target), `Duplicate link mapping: ${item.target}`);
      mapping.set(item.target, item.url);
    }
  }
  const localLinks = new Map(), resolutions = new Map();
  const resolve = async original => {
    if (resolutions.has(original)) return resolutions.get(original);
    const value = mapping.has(original) ? mapping.get(original) : original;
    if (mapping.has(original)) used.add(original);
    let uri;
    if (value.startsWith('https://')) uri = githubURL(value);
    else {
      const binding = localLink(value, modelName);
      const bytes = await read(binding.source_path);
      Object.assign(binding, {bytes: bytes.length, sha256: sha(bytes)});
      localLinks.set(binding.uri, binding); uri = binding.uri;
    }
    resolutions.set(original, uri); return uri;
  };
  const assets = new Map(), slides = [];
  for (const slide of model.slides) {
    const objects = new Map(slide.objects.map(object => [object.id, object]));
    const refs = [];
    for (const ref of slide.source_refs) refs.push({...ref, url: await resolve(ref.target)});
    const resolved = [];
    for (const object of slide.objects) {
      const expected = {...object};
      if (object.link_target) expected.resolved_link = await resolve(object.link_target);
      if (object.kind === 'arrow') expected.route = arrowRoute(object, objects);
      if (object.kind === 'image') {
        const assetName = relativeName(path.posix.normalize(path.posix.join(path.posix.dirname(modelName), object.path)));
        const bytes = await read(assetName);
        const png = bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
        const jpeg = bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
        check((png && object.path.endsWith('.png')) || (jpeg && /\.jpe?g$/u.test(object.path)), `${object.id}: only original PNG/JPEG bytes with matching extension are supported`);
        expected.source_path = assetName;
        expected.media_sha256 = sha(bytes); expected.content_type = png ? 'image/png' : 'image/jpeg';
        assets.set(object.path, bytes);
      }
      resolved.push(expected);
    }
    const citations = [...refs];
    for (const object of resolved) if (object.link_target && !citations.some(ref => ref.target === object.link_target)) {
      citations.push({label: object.id, target: object.link_target, url: object.resolved_link});
    }
    const sourceNotes = citations.length ? '\n\nSources:\n' + citations.map(ref =>
      `${ref.label}: ${ref.target}${ref.target === ref.url ? '' : `\n[${ref.url}]`}`).join('\n') : '';
    slides.push({...slide, objects: resolved, resolved_refs: refs, exported_notes: slide.notes_en + sourceNotes});
  }
  for (const target of mapping.keys()) check(used.has(target), `Unused link-map entry: ${target}`);
  return {root, assets, plan: {schema_version: 'g6b3r1-export-plan-v1',
    model_path: modelName, manifest_path: manifestName,
    final_pptx_path: path.posix.join(path.posix.dirname(modelName), 'main.pptx'),
    local_links: [...localLinks.values()],
    manifest_sha256: sha(manifestBytes), model_sha256: sha(modelBytes),
    source_files_verified: rows.size, model, slides}};
}

async function runtime() {
  const skill = process.env.SKILL_DIR, python = process.env.RUNTIME_PYTHON;
  check(skill && path.isAbsolute(skill) && python && path.isAbsolute(python), 'Set absolute SKILL_DIR and RUNTIME_PYTHON from the installed Work runtime');
  const helpers = await import(pathToFileURL(path.join(skill, 'container_tools/runtime_helpers.mjs')).href);
  const nm = await helpers.runtimeNodeModules();
  const version = JSON.parse(await fs.readFile(path.join(nm, '@oai/artifact-tool/package.json'), 'utf8')).version;
  check(version === '2.8.74', `Work preflight covered artifact-tool 2.8.74, found ${version}; requalification required`);
  const api = await helpers.importRuntimeModule('@oai/artifact-tool');
  const registries = [];
  for (const name of ['skia-canvas', '@napi-rs/canvas']) {
    try {
      const module = await helpers.requireRuntimeModule(name);
      const families = name === 'skia-canvas' ? module.FontLibrary?.families : module.GlobalFonts?.families?.map(item => item.family);
      if (Array.isArray(families)) registries.push({name, nimbus: families.includes('Nimbus Sans')});
    } catch { /* A second installed renderer registry may still establish availability. */ }
  }
  check(registries.some(registry => registry.nimbus), 'Exact Nimbus Sans is unavailable in the installed renderer font registries; no substitution allowed');
  const fontFiles = [];
  for (const style of ['Regular', 'Bold']) {
    const result = execFileSync('fc-match', ['--format', '%{family}\t%{style}\t%{file}\n', `Nimbus Sans:style=${style}`], {encoding: 'utf8'}).trim();
    const [family, actualStyle, file, ...extra] = result.split('\t');
    check(extra.length === 0 && family?.split(',').map(s => s.trim()).includes('Nimbus Sans') && file,
      `Exact Nimbus Sans ${style} is unavailable: ${result}`);
    check(style === 'Bold' ? /bold/iu.test(actualStyle) : /regular|normal|roman/iu.test(actualStyle), `Nimbus Sans ${style} resolved to ${actualStyle}`);
    fontFiles.push({style, family, actualStyle, sha256: sha(await fs.readFile(file))});
  }
  return {skill, python, api, fontEvidence: {registries, fontFiles}, version};
}

async function writeJSON(filename, value) {
  await fs.writeFile(filename, `${JSON.stringify(value, null, 2)}\n`, {flag: 'wx'});
}

async function build(context, run, rt) {
  await fs.mkdir(run); await fs.mkdir(path.join(run, 'build')); await fs.mkdir(path.join(run, 'qa'));
  const planPath = path.join(run, 'build/export_plan.json');
  const plan = context.plan;
  // The marker is a standalone installed-runtime command, immediately before authoring.
  execFileSync(process.execPath, [path.join(rt.skill, 'container_tools/mark_artifact_operation_started.mjs'),
    '--operation-kind', 'create', '--expected-output-count', '1', '--output-format', 'pptx'], {cwd: rt.skill, stdio: 'inherit'});
  const {Presentation, PresentationFile} = rt.api;
  const presentation = Presentation.create({slideSize: {width: 1280, height: 720}});
  for (const data of plan.slides) {
    const slide = presentation.slides.add(), shapes = new Map();
    const titleId = data.objects.find(object => object.kind === 'text' && titleMatches(object.text, data.title)).id;
    slide.background.fill = '#FFFFFF';
    for (const object of data.objects) {
      if (object.kind === 'arrow' && !object.route.unconnected) continue;
      const [left, top, width, height] = objectBox(object);
      const position = {left, top, width, height,
        ...(['line', 'arrow'].includes(object.kind) ? {horizontalFlip: object.w < 0, verticalFlip: object.h < 0} : {})};
      if (object.kind === 'image') {
        slide.images.add({blob: new Uint8Array(context.assets.get(object.path)), contentType: object.content_type,
          alt: object.alt, fit: 'contain', position});
        continue;
      }
      const isText = object.kind === 'text', isLine = object.kind === 'line' || object.kind === 'arrow';
      const shape = slide.shapes.add({name: object.id,
        geometry: isText ? 'textbox' : isLine ? 'line' : object.kind, position,
        fill: isText || isLine ? 'none' : object.fill,
        line: {fill: isText ? 'none' : isLine ? object.color : object.stroke,
          width: isText ? 0 : object.stroke_width},
        ...(isText && object.id === titleId ? {placeholderType: 'title'} : {})});
      shapes.set(object.id, shape);
      if (isText) {
        shape.text = object.text;
        shape.text.style = {typeface: 'Nimbus Sans', fontSize: object.font_px, bold: object.bold,
          color: object.color, alignment: object.align ?? 'left', verticalAlignment: 'top',
          autoFit: 'none', wrap: 'none', insets: {left: 0, right: 0, top: 0, bottom: 0}};
      }
    }
    for (const object of data.objects.filter(item => item.kind === 'arrow' && !item.route.unconnected)) {
      const from = shapes.get(object.source_id), to = shapes.get(object.target_id);
      object.route.fromIdx = slide.shapes.getConnectionSiteIndex(from, object.route.fromSide);
      object.route.toIdx = slide.shapes.getConnectionSiteIndex(to, object.route.toSide);
      check(Number.isInteger(object.route.fromIdx) && Number.isInteger(object.route.toIdx), `${object.id}: missing native connection site`);
      slide.shapes.connect(from, to, {kind: 'straight',
        fromIdx: object.route.fromIdx, toIdx: object.route.toIdx,
        line: {fill: object.color, width: object.stroke_width},
        tail: {type: 'triangle', width: 'med', length: 'med'}});
    }
    slide.speakerNotes.textFrame.setText(data.exported_notes);
  }
  await writeJSON(planPath, plan);
  await writeJSON(path.join(run, 'qa/runtime.json'), {artifact_tool: rt.version, node: process.version, font: rt.fontEvidence});
  const draft = path.join(run, 'build/main.draft.pptx'), linked = path.join(run, 'build/main.linked.pptx');
  await (await PresentationFile.exportPptx(presentation)).save(draft);
  execFileSync(rt.python, [path.join(HERE, 'attach_links.py'), 'attach', '--plan', planPath,
    '--presentation-root', context.root,
    '--input', draft, '--output', linked, '--report', path.join(run, 'qa/linked.native.json')], {stdio: 'inherit'});
  return {status: 'BUILT_STRUCTURAL_ONLY_RENDER_PENDING', draft, linked,
    remaining: ['finalizer', 'final OOXML reinspection', 'final PPTX render', 'per-slide comparison and reader review']};
}

async function finalize(context, run, rt) {
  const planPath = path.join(run, 'build/export_plan.json');
  const stored = parseJSON(await fs.readFile(planPath, 'utf8'));
  check(stored.model_sha256 === context.plan.model_sha256 && stored.manifest_sha256 === context.plan.manifest_sha256,
    'Build and finalization sources differ');
  const comparable = structuredClone(stored);
  for (const slide of comparable.slides) for (const object of slide.objects) if (object.route) {
    delete object.route.fromIdx; delete object.route.toIdx;
  }
  check(same(comparable, context.plan), 'Stored export plan differs from current verified source model');
  const candidate = path.join(run, 'build/main.linked.pptx');
  execFileSync(rt.python, [path.join(HERE, 'attach_links.py'), 'inspect', '--plan', planPath, '--input', candidate,
    '--presentation-root', context.root,
    '--report', path.join(run, 'qa/prefinal.native.json')], {stdio: 'inherit'});
  const {finalizePresentation} = await import(pathToFileURL(path.join(rt.skill, 'container_tools/artifact_tool_utils.mjs')).href);
  const finalPath = path.join(context.root, context.plan.final_pptx_path);
  under(context.root, finalPath);
  check(await fs.realpath(path.dirname(finalPath)) === path.dirname(finalPath), 'Final presentation directory cannot contain symlinks');
  const result = await finalizePresentation({workspaceDir: context.root, candidatePath: candidate, finalPath,
    pythonExecutable: rt.python,
    integrityValidatorPath: path.join(rt.skill, 'container_tools/inspect_presentation_package_integrity.py'),
    layoutValidatorPath: path.join(rt.skill, 'container_tools/inspect_presentation_layout_geometry.py'),
    layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-heading-fit'],
    explicitTotalSlideCount: context.plan.model.slides.length,
    requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [],
    fontPolicy: {basis: 'user_request', families: ['Nimbus Sans']}, verifyArtifactToolImport: true,
    receiptPath: path.join(run, 'qa/finalizer.json')});
  execFileSync(rt.python, [path.join(HERE, 'attach_links.py'), 'inspect', '--plan', planPath, '--input', finalPath,
    '--presentation-root', context.root,
    '--report', path.join(run, 'qa/final.native.json')], {stdio: 'inherit'});
  return {status: 'FINALIZED_STRUCTURAL_ONLY_VISUAL_REVIEW_PENDING', finalPath, sha256: result.finalSha256};
}

async function main() {
  const [mode, ...args] = process.argv.slice(2);
  check(['validate', 'build', 'finalize'].includes(mode), 'Usage: build_main.mjs validate|build|finalize --presentation-root DIR [--model FILE] [--manifest FILE] [--manifest-sha256 HEX] [--link-map FILE] [--run-dir DIR]');
  const options = {}, allowed = new Set(['presentation-root', 'model', 'manifest', 'manifest-sha256', 'link-map', 'run-dir']);
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].slice(2);
    check(args[i].startsWith('--') && allowed.has(key) && !Object.hasOwn(options, key) && args[i + 1], `Invalid/duplicate option: ${args[i]}`);
    options[key] = args[i + 1];
  }
  check(options['presentation-root'], '--presentation-root is required');
  const context = await prepare(options);
  if (mode === 'validate') {
    console.log(JSON.stringify({status: 'SOURCE_VALIDATED_ONLY_NO_EXPORT', slides: context.plan.slides.length,
      manifest_sha256: context.plan.manifest_sha256, source_files_verified: context.plan.source_files_verified,
      local_links_verified: context.plan.local_links.length, final_pptx_path: context.plan.final_pptx_path}));
    return;
  }
  check(options['run-dir'] && /^[0-9a-f]{64}$/u.test(options['manifest-sha256'] ?? ''), '--run-dir and externally recorded --manifest-sha256 are required for build/finalize');
  const runName = relativeName(options['run-dir']);
  const run = path.join(context.root, runName); under(context.root, run);
  check(await fs.realpath(path.dirname(run)) === path.dirname(run), 'Output parent must exist and cannot contain symlinks');
  if (mode === 'finalize') check((await fs.lstat(run)).isDirectory() && !(await fs.lstat(run)).isSymbolicLink(), 'Run directory must be a real directory');
  else check(!(await fs.stat(run).catch(error => { if (error.code === 'ENOENT') return null; throw error; })), 'Run directory already exists; preserve failed attempts and choose a new revision');
  const rt = await runtime();
  const result = mode === 'build' ? await build(context, run, rt) : await finalize(context, run, rt);
  // Revalidate after export as well; any concurrent source edit makes the run unusable.
  const after = await prepare(options);
  check(after.plan.manifest_sha256 === context.plan.manifest_sha256 && after.plan.model_sha256 === context.plan.model_sha256, 'Sources changed during export');
  console.log(JSON.stringify(result));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(`G6B3R1 exporter stopped: ${error.message}`); process.exitCode = 1; });
}
