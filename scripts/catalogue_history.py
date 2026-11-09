"""Reviewed reference dates and inclusive paper credits for catalogue families."""
from datetime import date
from functools import cache
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def date_key(value):
    """Keep recorded precision; zero sorts year-only records without inventing a day."""
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}(?:-\d{2}-\d{2})?', value):
        raise ValueError('Reference dates require YYYY or YYYY-MM-DD')
    if len(value) == 10:
        date.fromisoformat(value)
    elif not 1 <= int(value) <= 9999:
        raise ValueError('Invalid reference year')
    return tuple(map(int, value.split('-'))) + (0,) * (3 - len(value.split('-')))


@cache
def registry():
    data = json.loads((ROOT / 'catalogue-history.json').read_text())
    for key, reference in data['references'].items():
        date_key(reference['date'])
        if not reference['authors'] or not all(reference['authors']):
            raise ValueError(f'Missing paper authors: {key}')
        if reference['kind'] not in {'arxiv', 'publication'} or not reference['url'].startswith('https://'):
            raise ValueError(f'Missing reference date evidence: {key}')
    for label, record in data['examples'].items():
        keys = record['references']
        background = record['background_references']
        if not record['name'] or not keys or len(set(keys)) != len(keys):
            raise ValueError(f'Invalid catalogue history: {label}')
        if set(keys) - data['references'].keys() or set(background) - set(keys):
            raise ValueError(f'Unregistered reference in catalogue history: {label}')
        if not set(keys) - set(background) or not all(background.values()):
            raise ValueError(f'Catalogue family needs a reference discussing the example: {label}')
    return data


def history(label):
    data = registry()
    record = data['examples'][label]
    references = [dict(data['references'][key], key=key,
                       background=record['background_references'].get(key, ''))
                  for key in record['references']]
    references.sort(key=lambda reference: date_key(reference['date']))
    earliest = next(reference for reference in references if not reference['background'])
    credits = '; '.join('–'.join(reference['authors']) + ', ' + reference['date'][:4]
                        for reference in references)
    title = record['name'] + (' (' + credits + ')' if len(references) > 1 else '')
    return {'title': title, 'name': record['name'], 'date': earliest['date'],
            'earliest_reference': earliest['key'], 'references': references}


def apply(records, topics, entries):
    """Rename the reading edition after source arrangement, keeping its routes and tags."""
    if not records:
        return
    if {record['label'] for record in records} != set(registry()['examples']):
        raise ValueError('Every catalogue family needs exactly one history record')
    for record in records:
        item = history(record['label'])
        topic = topics[record['section']]
        original_title = topic['title']
        topic.update(title=item['title'], chronology=item)
        record.update(title=item['title'], chronology=item)
        for entry in entries.values():
            if entry['topic'] == record['section'] and (entry.get('section_intro') or entry['tag'] == record['tag']):
                entry.update(section_source_title=original_title, section_title=item['title'])


def panel(item):
    earliest = next(reference for reference in item['references'] if reference['key'] == item['earliest_reference'])
    kind = 'first arXiv submission' if earliest['kind'] == 'arxiv' else 'publication year'
    rows = []
    for reference in item['references']:
        authors = '–'.join(reference['authors'])
        basis = 'first arXiv submission' if reference['kind'] == 'arxiv' else 'publication year'
        qualification = ' Background only: ' + reference['background'] if reference['background'] else ''
        rows.append(f'<li><a href="{escape(reference["url"], quote=True)}">{escape(authors)}</a> '
                    f'— {reference["date"]} ({basis}).{escape(qualification)}</li>')
    return (f'<div class="catalogue-history"><p>Earliest recorded reference: '
            f'<time datetime="{item["date"]}">{item["date"]}</time> ({kind}).</p>'
            '<details><summary>Paper credits and chronology</summary>'
            '<p>Paper credits are chronological and include every author of the cited papers. '
            'They identify sources, not exclusive discovery credit. Background-only citations do not determine '
            'the date of this example. A classical example may predate the references recorded here.</p><ol>'
            + ''.join(rows) + '</ol></details></div>')
