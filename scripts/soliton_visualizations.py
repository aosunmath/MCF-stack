"""Attach reviewed mathematical illustrations to permanent catalogue entries."""
from functools import cache
from html import escape
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[1]


@cache
def registry():
    path = ROOT / 'catalogue-visualizations.json'
    if not path.exists():
        return {}
    records = json.loads(path.read_text())['entries']
    result = {item['label']: item for item in records}
    if len(result) != len(records):
        raise ValueError('Repeated catalogue visualization label')
    return result


def visualization(label, root):
    item = registry().get(label)
    if not item:
        return ''
    figures = [render_figure(figure, root) for figure in [item, *item.get('supplementary', [])]]
    for experiment in experiments(item):
        url = escape(root + experiment['path'], quote=True)
        title = escape(experiment['title'])
        anchor = escape(experiment.get('id', item['model']), quote=True)
        figures.append(f'''<section id="experiment-{anchor}" class="soliton-experiment" aria-label="{title}">
<h3>{title}</h3>
<p><strong>Numerical experiment.</strong> {escape(experiment['caption'])}</p>
<p><a href="{url}" target="_blank" rel="noopener">Open full-page visualization ↗</a></p>
<details open><summary>Explore the interactive flow</summary>
<iframe src="{url}" title="{title}" loading="lazy" sandbox="allow-scripts" referrerpolicy="no-referrer"></iframe>
</details></section>''')
    return '\n'.join(figures)


def experiments(item):
    """Keep the original experiment and its permanent anchor when adding others."""
    return ([item['experiment']] if item.get('experiment') else []) + item.get('additional_experiments', [])


def render_figure(item, root):
    assets = root + 'assets/solitons/'
    alt, caption = escape(item['alt'], quote=True), escape(item['caption'])
    status = escape(item['status'])
    drawing_link = f' <a href="{assets}{item["model"]}.svg">Open drawing</a>'
    for drawing in item.get('additional_drawings', []):
        drawing_link += f' · <a href="{assets}{escape(drawing["model"], quote=True)}.svg">{escape(drawing["title"])}</a>'
    credit_anchor = escape(item.get('credit_anchor', 'methods'), quote=True)
    drawing_link += f' · <a href="{root}numerical-references/#{credit_anchor}">Numerical references and credits</a>'
    image = f'<img src="{assets}{item["model"]}.svg" alt="{alt}" loading="lazy" width="640" height="410">'
    if item.get('interactive'):
        return f'''<figure class="soliton-figure" data-soliton="{assets}{item['model']}.json">
<div class="soliton-stage">{image}<canvas hidden tabindex="0" role="img" aria-label="Interactive geometry: {alt}. Arrow keys rotate; plus and minus zoom."></canvas></div>
<div class="soliton-controls" hidden><button type="button" data-view-action="in" aria-label="Zoom in">Zoom +</button><button type="button" data-view-action="out" aria-label="Zoom out">Zoom −</button><button type="button" data-view-action="reset">Reset view</button><button type="button" data-view-action="wire" aria-pressed="false">Mesh</button></div>
<p class="soliton-help" hidden>Drag to rotate. Use the zoom buttons, or focus the drawing and use arrow keys and + / −.</p>
<figcaption><strong>{status}.</strong> {caption}{drawing_link}</figcaption><p class="soliton-status" role="status"></p></figure>'''
    return f'<figure class="soliton-figure"><div class="soliton-stage">{image}</div><figcaption><strong>{status}.</strong> {caption}{drawing_link}</figcaption></figure>'


def validate_visualizations(entries, destination):
    labels = {variant['label'] for entry in entries.values() for variant in entry['variants'] if variant['source'] == 'gmt-foundations'}
    if not labels:
        return
    for label, item in registry().items():
        if label not in labels:
            raise ValueError('Visualization has no mathematical entry: ' + label)
        if item['category'] not in {'shrinkers', 'translators', 'expanders', 'other-special-flows'}:
            raise ValueError('Invalid solution category: ' + label)
        for figure in [item, *item.get('supplementary', [])]:
            validate_figure(figure, label, destination)
        anchors = set()
        for experiment in experiments(item):
            anchor = experiment.get('id', item['model'])
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', anchor) or anchor in anchors:
                raise ValueError('Invalid or repeated numerical experiment anchor: ' + label)
            anchors.add(anchor)
            path = PurePosixPath(experiment['path'])
            if path.is_absolute() or '..' in path.parts or '\\' in str(path) or path.suffix != '.html':
                raise ValueError('Invalid numerical experiment path: ' + label)
            if not (destination / path).is_file():
                raise ValueError('Missing numerical experiment: ' + label)


def validate_figure(item, label, destination):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item.get('credit_anchor', 'methods')):
        raise ValueError('Invalid figure credit anchor: ' + label)
    for suffix in (['.svg', '.json'] if item.get('interactive') else ['.svg']):
        path = destination / 'assets' / 'solitons' / (item['model'] + suffix)
        if not path.is_file():
            raise ValueError('Missing catalogue illustration: ' + str(path))
    if item.get('interactive'):
        data = json.loads((destination / 'assets' / 'solitons' / (item['model'] + '.json')).read_text())
        n = len(data['vertices'])
        if not n or any(i < 0 or i >= n for face in data['faces'] + data['paths'] for i in face):
            raise ValueError('Invalid geometry indices: ' + label)
        if data['status'] in {'numerical-ode', 'numerical-pde'} and 'Numerical' not in item['status']:
            raise ValueError('Numerical geometry must be labeled: ' + label)

    for variant in item.get('additional_drawings', []):
        validate_figure({**item, 'model': variant['model'], 'additional_drawings': []}, label, destination)
