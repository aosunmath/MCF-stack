import copy
import json
from pathlib import Path
import sys
import unittest

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalogue_properties import ambient_memberships, arrange_by_ambient, panel, registry
from reader import Reader
from soliton_visualizations import registry as illustrations


class AmbientArrangementTests(unittest.TestCase):
    def setUp(self):
        self.chapters = {c['slug']: {**c, 'number': i} for i, c in enumerate(json.loads((ROOT / 'collection.json').read_text())['chapters'], 1)}
        self.records = [{**record, 'section': illustrations()[label]['section'], 'category': illustrations()[label]['category']}
                        for label, record in registry().items()]

    def test_every_family_has_one_primary_position_and_all_other_spaces_link_back(self):
        original = copy.deepcopy(self.chapters)
        arrange_by_ambient(self.chapters, self.records)
        for key, chapter in self.chapters.items():
            if key == 'orientation':
                self.assertEqual(chapter, original[key])
                continue
            placed = [topic for group in chapter['ambient_groups'] for topic in group['topics']]
            self.assertCountEqual(placed, original[key]['topics'])
            self.assertEqual(len(placed), len(set(placed)))
            self.assertEqual(chapter['topics'], placed)
            for group in chapter['ambient_groups']:
                self.assertEqual([placed.index(r['section']) for r in group['related']], sorted(placed.index(r['section']) for r in group['related']))
            for topic, spaces in chapter['ambient_families'].items():
                primary = next(iter(spaces))
                group = next(g for g in chapter['ambient_groups'] if topic in g['topics'])
                self.assertEqual(group['key'], primary)
                linked = {g['key'] for g in chapter['ambient_groups'] if any(r['section'] == topic for r in g['related'])}
                self.assertEqual(linked, set(spaces) - {primary})
                # Family order within a dimension remains the reviewed source order.
                self.assertEqual(group['topics'], [t for t in original[key]['topics'] if t in group['topics']])
        self.assertEqual(self.chapters['shrinkers']['topics'][:3], ['round-shrinking-spheres', 'planes-through-the-shrinker-center', 'abresch-langer-closed-shrinking-curves'])
        self.assertEqual(self.chapters['other-special-flows']['topics'][0], 'the-angenent-oval-as-an-explicit-ancient-flow')

    def test_dimension_restrictions_and_curved_spaces_are_not_inferred(self):
        self.assertEqual(list(ambient_memberships(registry()['ex:catalogue-eternal-helices'])), ['r3', 'higher'])
        self.assertEqual(list(ambient_memberships(registry()['ex:catalogue-curve-products'])), ['r4', 'higher'])
        self.assertEqual(list(ambient_memberships(registry()['ex:catalogue-double-sphere-flow'])), ['manifold'])

    def test_chapter_links_target_real_cases_and_primary_reading_routes_stay_unique(self):
        arrange_by_ambient(self.chapters, self.records)
        topics = {topic: {'title': topic} for chapter in self.chapters.values() for topic in chapter['topics']}
        reader = Reader(self.chapters, topics, {}, {}, {'enabled': False})
        self.assertEqual(len(reader.order), len(set(reader.order)))
        self.assertEqual(reader.sections['abresch-langer-closed-shrinking-curves']['number'], '2.3')
        for record in self.records:
            soup = BeautifulSoup(panel(record['label'], '../../'), 'html.parser')
            for cases in ambient_memberships(record).values():
                for case in cases:
                    self.assertIsNotNone(soup.find('details', id=case['anchor']))
        for key, chapter in self.chapters.items():
            if key == 'orientation':
                continue
            soup = BeautifulSoup(reader.section_list(key, '../../', anchors=True, subsections=True), 'html.parser')
            primary = soup.select('.section-list > li > a:first-child')
            self.assertEqual(len(primary), len(chapter['topics']))
            self.assertEqual(len({a['href'] for a in primary}), len(primary))
            ids = [node['id'] for node in soup.select('[id]')]
            self.assertEqual(len(ids), len(set(ids)))
            for anchor in soup.select('.ambient-also a'):
                self.assertIn(anchor['href'][1:], ids)
            section_records = {r['section']: r for r in self.records}
            for anchor in soup.select('.ambient-related a'):
                path, fragment = anchor['href'].split('#')
                record = section_records[path.rstrip('/').split('/')[-1]]
                self.assertIsNotNone(BeautifulSoup(panel(record['label'], '../../'), 'html.parser').find(id=fragment))

    def test_ambiguous_and_missing_family_metadata_fail_before_numbering(self):
        with self.assertRaisesRegex(ValueError, 'one catalogue family'):
            arrange_by_ambient(self.chapters, self.records + [self.records[0]])
        with self.assertRaisesRegex(ValueError, 'needs property metadata'):
            arrange_by_ambient(self.chapters, self.records[1:])


if __name__ == '__main__':
    unittest.main()
