from pathlib import Path
import json
import sys
import tempfile
import unittest

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from chapter_overviews import load_overviews
from collection import prepare_fragment
from reader_references import page_references


class ChapterOverviewTests(unittest.TestCase):
    def test_absent_registry_is_optional(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(load_overviews(folder), {})

    def test_registry_rejects_escaping_paths_and_duplicate_chapters(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'overview.html').write_text('<h2 id="equation">Equation</h2>')
            entry = {'slug': 'sample', 'file': 'overview.html'}
            for chapters in ([entry, entry], [{'slug': 'sample', 'file': '../private.html'}]):
                (root / 'chapter-overviews.json').write_text(json.dumps({'version': 1, 'chapters': chapters}))
                with self.assertRaises(ValueError):
                    load_overviews(root)

    def test_overview_citations_use_shared_page_references(self):
        fragment = prepare_fragment({'source': 'sample', 'label': 'overview', 'html': '<h2 id="geometry">Geometry</h2><a href="#geometry">Jump</a><a href="/bibliography/Paper">Paper</a>'}, {}, {('sample', 'Paper'): 'R123'}, '../../')
        rendered, used = page_references(fragment, {'R123': {'html': 'A paper', 'sources': [{'source': 'sample', 'key': 'Paper'}]}}, '../../')
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertIsNotNone(soup.select_one('h2#sample-geometry'))
        self.assertIsNotNone(soup.select_one('a[href="#sample-geometry"]'))
        self.assertEqual(used, ['R123'])
        self.assertIsNotNone(soup.select_one('a[data-reference="R123"][href="#reference-R123"]'))
        self.assertIsNotNone(soup.select_one('a[href="#cite-R123-1"]'))

    def test_registered_prose_has_only_current_category_chapters(self):
        overviews = load_overviews(ROOT / 'content/gmt-foundations')
        self.assertEqual(set(overviews), {'shrinkers', 'translators', 'expanders', 'other-special-flows'})
        for overview in overviews.values():
            soup = BeautifulSoup(overview['html'], 'html.parser')
            self.assertTrue(soup.select('a[href^="/bibliography/"]'))
            self.assertFalse(soup.select('h1, script, iframe'))
