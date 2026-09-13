"""Offline HTML report of actual Testflix artifacts, without provider calls."""
from html import escape
import json
from pathlib import Path


def _text(value):
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
    return escape(str(value))


def _table(headers, rows):
    return '<div class="table"><table><thead><tr>'+''.join('<th>'+_text(h)+'</th>' for h in headers)+\
        '</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+_cell(v)+'</td>' for v in row)+\
        '</tr>' for row in rows)+'</tbody></table></div>'


def _cell(value):
    text = _text(value)
    if len(text) <= 600:
        return text
    count = len(value) if isinstance(value, (dict, list, tuple)) else None
    label = 'Evidence record' + (' | %s fields' % count if isinstance(value, dict) else
        ' | %s entries' % count if count is not None else '')
    return '<details><summary>'+label+'</summary><pre>'+text+'</pre></details>'


def render_v01(story, path):
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>Testflix | Execution record</title><style>',
        '*{box-sizing:border-box}body{margin:0;color:#20272d;background:#fff;font:14px/1.5 system-ui,sans-serif}',
        'header,main,footer{max-width:1180px;margin:auto;padding:24px}header{border-bottom:3px solid #227654}',
        'h1{font-size:30px;margin:0}h2{font-size:20px;margin:0 0 12px}h3{font-size:16px}',
        'section{padding:24px 0;border-bottom:1px solid #d6dce0}p{max-width:88ch}',
        '.table{overflow-x:auto}table{border-collapse:collapse;width:100%;table-layout:fixed}',
        'th,td{text-align:left;vertical-align:top;border-bottom:1px solid #d6dce0;padding:10px;overflow-wrap:anywhere;white-space:pre-wrap}',
        'th{background:#edf2f4}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.5 ui-monospace,monospace}',
        'summary{cursor:pointer;color:#195c8d;padding:10px 0}footer{color:#535f66}',
        '.status{font-weight:600;color:#227654}.pending{color:#9a3a22}',
        '@media(max-width:600px){header,main,footer{padding:16px}h1{font-size:26px}th,td{padding:7px;font-size:12px}}',
        '</style><header><h1>Testflix</h1><p>Execution record | '+_text(story['recorded_utc'])+'</p>',
        '<p class="status">'+_text(story['status'])+'</p></header><main>',
        '<section><h2>Provenance</h2><p>'+_text(story['provenance'])+'</p>',
        _table(('Evidence', 'Actual result'), story['provenance_rows']), '</section>',
        '<section><h2>Request and semantic duties</h2>',
        _table(('Branch', 'Request', 'Consumed plan'), story['requests'])]
    for branch in story['semantic_branches']:
        parts.append('<h3>'+_text(branch['name'])+'</h3>')
        for record in branch['records']:
            parts.extend(('<details><summary>'+_text(record['role'])+'</summary>',
                '<pre>'+_text(dict(output=record['output'], capture=record['capture'],
                    input_projection=record['projection']))+'</pre></details>'))
    parts.extend(('</section><section><h2>Four independent Roots</h2>',
        _table(('Root', 'Decision / operation', 'Evidence reference'), story['roots']),
        '</section><section><h2>Controlled continuation</h2>',
        _table(('Stage', 'Actual result', 'Evidence'), story['controlled_stages']),
        '</section><section><h2>Live and captured history</h2>',
        _table(('Branch / stage', 'Result', 'Time / reference'), story['live_stages']),
        '</section><section><h2>Validation and replay</h2>',
        _table(('Control', 'Result', 'Scope'), story['controls']),
        '</section><section><h2>Remaining obligations</h2><p class="pending">'+
            _text(story['remaining'])+'</p></section></main>',
        '<footer>Root remains the sole action authority. Captures and replay do not grant current permission. '
            'No owner apply, commit or push was performed.</footer></html>'))
    with Path(path).open('x') as stream:
        stream.write(''.join(parts))
    return Path(path)
