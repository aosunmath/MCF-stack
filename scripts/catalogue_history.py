"""Reference chronology and source-checked construction credits for catalogue families."""
from datetime import date
from functools import cache
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CONSTRUCTION_ROLES = {'construction', 'alternative-construction', 'numerical-construction'}
REVIEW_ROLES = CONSTRUCTION_ROLES | {'analysis', 'survey', 'background', 'prior-construction', 'unreviewed'}


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
        if reference['kind'] not in {'arxiv', 'preprint', 'publication'} or not reference['url'].startswith('https://'):
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
        reviews = record.get('credit_reviews', {})
        if (len(keys) > 1 and set(reviews) != set(keys)) or set(reviews) - set(keys):
            raise ValueError(f'Multi-paper title credits need a decision for every reference: {label}')
        for key, review in reviews.items():
            if review.get('role') not in REVIEW_ROLES or not review.get('locator') or not review.get('note'):
                raise ValueError(f'Title credit needs a source passage and contribution: {label}, {key}')
            if key in background and review['role'] in CONSTRUCTION_ROLES:
                raise ValueError(f'A background source cannot construct this example: {label}, {key}')
            if 'reviewed_url' in review and not review['reviewed_url'].startswith('https://'):
                raise ValueError(f'Invalid reviewed source URL: {label}, {key}')
    return data


def history(label):
    data = registry()
    record = data['examples'][label]
    references = [dict(data['references'][key], key=key,
                       background=record['background_references'].get(key, ''),
                       credit_review=record.get('credit_reviews', {}).get(key))
                  for key in record['references']]
    references.sort(key=lambda reference: date_key(reference['date']))
    earliest = next(reference for reference in references if not reference['background'])
    constructors = [reference for reference in references
                    if reference['credit_review'] and reference['credit_review']['role'] in CONSTRUCTION_ROLES]
    credits = '; '.join('–'.join(reference['authors']) + ', ' + reference['date'][:4]
                        for reference in constructors)
    title = record['name'] + (' (' + credits + ')' if credits else '')
    return {'title': title, 'name': record['name'], 'date': earliest['date'],
            'earliest_reference': earliest['key'], 'references': references,
            'construction_references': [reference['key'] for reference in constructors]}


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
    rows = []
    for reference in item['references']:
        authors = '–'.join(reference['authors'])
        basis = {'arxiv': 'first arXiv submission', 'preprint': 'preprint year',
                 'publication': 'publication year'}[reference['kind']]
        qualification = ' Background only: ' + reference['background'] if reference['background'] else ''
        review = reference.get('credit_review')
        if review:
            role = review['role'].replace('-', ' ').capitalize()
            qualification += f' {role}: {review["note"]} Passage: {review["locator"]}.'
        reviewed_link = (' <a href="' + escape(review['reviewed_url'], quote=True) + '">Reviewed text</a>.'
                         if review and review.get('reviewed_url') else '')
        rows.append(f'<li><a href="{escape(reference["url"], quote=True)}">{escape(authors)}</a> '
                    f'— {reference["date"]} ({basis}).{escape(qualification)}{reviewed_link}</li>')
    return ('<div class="catalogue-history"><details><summary>Paper credits and chronology</summary>'
            '<p>Title credits include all authors of papers with a reviewed construction of this example, '
            'in chronological order. Later analysis, surveys, and citations remain listed here; they do not '
            'by themselves earn construction credit. Alternative and numerical constructions are qualified below. '
            'These credits are not an exhaustive discovery history. Background-only citations do not determine '
            'the date of this example. A classical example may predate the references recorded here.</p><ol>'
            + ''.join(rows) + '</ol></details></div>')
