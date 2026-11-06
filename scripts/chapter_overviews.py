"""Load explicitly registered chapter prose from a manuscript snapshot."""
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup


def load_overviews(source):
    source = Path(source).resolve()
    registry = source / 'chapter-overviews.json'
    if not registry.exists():
        return {}
    data = json.loads(registry.read_text())
    if data.get('version') != 1:
        raise ValueError('Unsupported chapter overview registry')
    result = {}
    for item in data['chapters']:
        slug, name = item['slug'], item['file']
        path = (source / name).resolve()
        if (not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug)
                or slug in result or path.suffix != '.html'
                or not path.is_relative_to(source)):
            raise ValueError('Invalid or duplicate chapter overview')
        html = path.read_text()
        soup = BeautifulSoup(html, 'html.parser')
        ids = [node['id'] for node in soup.select('[id]')]
        if len(ids) != len(set(ids)) or not soup.select('h2[id]'):
            raise ValueError('Chapter overviews need unique heading anchors')
        result[slug] = {'html': html, 'file': name}
    return result
