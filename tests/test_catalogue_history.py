import json
from pathlib import Path
import re
import sys
import unittest

from bs4 import BeautifulSoup
from pybtex.database import parse_file

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue_history as history
from catalogue_properties import registry as properties
from numbering import assign_numbers


class CatalogueHistoryTests(unittest.TestCase):
    def test_every_example_and_every_cited_paper_is_reviewed(self):
        registry = history.registry()
        self.assertEqual(set(registry['examples']), set(properties()))
        bibliography = parse_file(ROOT / 'content/gmt-foundations/references.bib')
        for path in (ROOT / 'content/gmt-foundations').glob('catalogue*.tex'):
            for block in re.split(r'(?=\\chapter\{)', path.read_text()):
                match = re.search(r'\\label\{(ex:catalogue-[^}]+)\}', block)
                if not match:
                    continue
                label = match.group(1)
                cited = {key.strip() for keys in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}', block) for key in keys.split(',')}
                self.assertEqual(cited, set(registry['examples'][label]['references']), label)
        for key, reference in registry['references'].items():
            self.assertIn(key, bibliography.entries)
            self.assertEqual(len(reference['authors']), len(bibliography.entries[key].persons['author']))
            self.assertLessEqual(int(reference['date'][:4]), int(bibliography.entries[key].fields['year']))

    def test_first_preprints_override_later_editions(self):
        for label, expected in [('kkm-one-end', '2011-06-27'), ('bns-genus', '2021-10-12'),
                                ('drugan-sphere', '2013-03-29'), ('hmw-one-ended', '2025-02-27'),
                                ('ancient-torus-curves', '2012-07-17')]:
            self.assertEqual(history.history('ex:catalogue-' + label)['date'], expected)
        item = history.history('ex:catalogue-eternal-helices')
        self.assertEqual([r['key'] for r in item['references']], ['CatAAAW13', 'CatSS19'])
        self.assertIn('D. J. Altschuler–S. J. Altschuler–Angenent–Wu, 2012; Stryker–Sun, 2019', item['title'])

    def test_background_theorems_and_shrinker_factors_do_not_backdate_constructions(self):
        for label, expected in [('moller-genus', '2011-11-30'), ('sun-wang-torus-translators', '2023-01-19'),
                                ('sun-wang-sphere-doubling-translators', '2023-01-19'),
                                ('translating-annuloids', '2023-08-04'), ('angenent-torus-cylinders', '2026-07-26')]:
            self.assertEqual(history.history('ex:catalogue-' + label)['date'], expected)
        item = history.history('ex:catalogue-sun-wang-torus-translators')
        panel = BeautifulSoup(history.panel(item), 'html.parser')
        self.assertIn('Background only', panel.get_text())
        self.assertEqual(len(panel.select('li')), len(item['references']))

    def test_credits_are_chronological_and_complete(self):
        for label in history.registry()['examples']:
            item = history.history(label)
            dates = [history.date_key(r['date']) for r in item['references']]
            self.assertEqual(dates, sorted(dates))
            if len(item['references']) > 1:
                for r in item['references']:
                    for author in r['authors']:
                        self.assertIn(author, item['title'])

    def test_year_only_dates_keep_their_precision(self):
        self.assertEqual(history.history('ex:catalogue-abresch-langer')['date'], '1986')
        self.assertLess(history.date_key('2011'), history.date_key('2011-06-01'))
        for invalid in ['2011-06', '2011-02-30', 'unknown']:
            with self.assertRaises(ValueError):
                history.date_key(invalid)

    def test_renaming_preserves_source_identity_and_absorbs_original_caption(self):
        label = 'ex:catalogue-eternal-helices'
        old = 'Eternal shrinking helices'
        records = [{'label': label, 'section': 'original-route', 'tag': 'EXAMPLE'}]
        topics = {'original-route': {'title': old}}
        variant = {'source': 'gmt-foundations', 'tag': 'SOURCE', 'label': label, 'kind': 'example', 'caption': old}
        entry = {'tag': 'EXAMPLE', 'topic': 'original-route', 'variants': [variant], 'section_example': True}
        # apply validates full catalogue coverage; exercise the title contract with all records.
        from unittest.mock import patch
        full = history.registry()
        with patch.object(history, 'registry', return_value={**full, 'examples': {label: full['examples'][label]}}):
            history.apply(records, topics, {'EXAMPLE': entry})
        refs = assign_numbers({'category': {'number': 5, 'topics': ['original-route']}}, {'EXAMPLE': entry})
        self.assertEqual(entry['topic'], 'original-route')
        self.assertEqual(entry['tag'], 'EXAMPLE')
        self.assertEqual(variant['caption'], old)
        self.assertTrue(refs['gmt-foundations', 'SOURCE']['repeated_caption'])
        self.assertIn('Stryker–Sun', entry['reader_title'])


if __name__ == '__main__':
    unittest.main()
