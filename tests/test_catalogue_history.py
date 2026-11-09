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
    def test_every_example_and_every_cited_paper_has_chronology(self):
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
        self.assertEqual(history.history('ex:catalogue-minimal-ancient-flows')['date'], '2019-04-17')
        item = history.history('ex:catalogue-sun-wang-torus-translators')
        panel = BeautifulSoup(history.panel(item), 'html.parser')
        self.assertIn('Background only', panel.get_text())
        self.assertEqual(len(panel.select('li')), len(item['references']))

    def test_only_reviewed_constructors_supply_chronological_title_credits(self):
        for label in history.registry()['examples']:
            item = history.history(label)
            dates = [history.date_key(r['date']) for r in item['references']]
            self.assertEqual(dates, sorted(dates))
            constructors = [r for r in item['references'] if r['key'] in item['construction_references']]
            expected = '; '.join('–'.join(r['authors']) + ', ' + r['date'][:4] for r in constructors)
            self.assertEqual(item['title'], item['name'] + (' (' + expected + ')' if expected else ''))
            for r in constructors:
                self.assertIn(r['credit_review']['role'], history.CONSTRUCTION_ROLES)
                self.assertTrue(r['credit_review']['locator'])
                self.assertTrue(r['credit_review']['note'])

    def test_surveys_and_later_analysis_do_not_receive_construction_credit(self):
        expected = {
            'angenent-torus': ['CatAngenent1992'],
            'mobius-shrinker': ['CatLeeWang2009'],
            'bns-genus': ['CatBNS2025'],
            'pitchfork': ['CatHMW20'],
            'scherk-translators': ['CatHMW20'],
            'translating-catenoid': ['CSS07'],
            'bowl-translator': [],
            'round-sphere': [],
            'network-spoon': [],
            'ancient-sine-wave': [],
        }
        for label, keys in expected.items():
            item = history.history('ex:catalogue-' + label)
            self.assertEqual(item['construction_references'], keys, label)
            panel = BeautifulSoup(history.panel(item), 'html.parser')
            self.assertEqual(len(panel.select('li')), len(item['references']))
            self.assertNotIn('Earliest recorded reference:', panel.get_text())
            self.assertFalse(panel.details.has_attr('open'))

    def test_a_paper_can_supply_existence_and_classification_or_independent_rediscovery(self):
        tridents = history.history('ex:catalogue-nguyen-tridents')
        self.assertEqual(tridents['construction_references'], ['CatNguyen09', 'CatHMWTridents22'])
        balls = history.history('ex:catalogue-free-boundary-ancient-balls')
        self.assertEqual(len(balls['construction_references']), 2)
        helices = history.history('ex:catalogue-eternal-helices')
        self.assertIn('acknowledges', history.panel(helices))

    def test_earliest_reference_need_not_be_a_constructor(self):
        item = history.history('ex:catalogue-pitchfork')
        self.assertEqual(item['earliest_reference'], 'CatHIMWNotes19')
        self.assertNotIn(item['earliest_reference'], item['construction_references'])
        self.assertEqual(item['date'], history.registry()['references']['CatHIMWNotes19']['date'])

    def test_year_only_dates_keep_their_precision(self):
        self.assertEqual(history.history('ex:catalogue-abresch-langer')['date'], '1984')
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
