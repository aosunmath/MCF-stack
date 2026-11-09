import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from collection import build_collection, check_links, continuous_section, global_tag, source_roots
from reader import Reader, bibtex
from project import TITLE, CONTRIBUTORS
from catalogue_properties import registry as property_registry


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.records = [{"tag": f"{n:08X}", "label": f"def:internal_label_{n}", "title": f"Definition 1.1.{n}", "semantic_title": f"Internal label {n}", "number": f"1.1.{n}", "caption": "", "kind": "definition", "topic": topic, "html": f'<article class="env-definition"><p>Definition 1.1.{n}. A statement.</p></article>'} for n, topic in enumerate(("Alpha", "Alpha", "Beta", "Gamma"), 1)]
        self.config = {"version": 1, "entries": [], "topics": [{"slug": name.lower(), "title": name} for name in ("Alpha", "Beta", "Gamma")], "chapters": [{"slug": "first", "title": "First chapter", "topics": ["alpha", "beta"]}, {"slug": "second", "title": "Second chapter", "topics": ["gamma"]}]}
        self.book = {"slug": "source", "title": "Test source", "author": "Test author", "status": "published", "repository": "https://github.com/example/source"}

    def build(self, root):
        folder = root / "books" / "source"
        folder.mkdir(parents=True)
        for name, value in (("entries", self.records), ("references", []), ("tags", [{"tag": r["tag"], "page": f'tag/{r["tag"]}/index.html'} for r in self.records]), ("edition", {"commit": "a" * 40})):
            (folder / (name + ".json")).write_text(json.dumps(value))
        shutil.copytree(ROOT / "site" / "assets", root / "assets")
        (root / "assets" / "mathjax").mkdir()
        (root / "assets" / "mathjax" / "tex-chtml.js").touch()
        build_collection([self.book], root, self.config)
        return json.loads((root / "navigation.json").read_text())

    def test_chapters_list_sections_and_sections_show_full_statements(self):
        self.config["topics"][0]["description"] = "A redundant section summary."
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.build(root)
            chapter = BeautifulSoup((root / "chapters/first/index.html").read_text(), "html.parser")
            self.assertEqual(len(chapter.select('main .section-list a')), 2)
            self.assertFalse(chapter.select('main .reference-entry'))
            section = BeautifulSoup((root / "sections/alpha/index.html").read_text(), "html.parser")
            self.assertFalse(section.select('main .reference-entry'))
            self.assertNotIn('A redundant section summary.', section.select_one('main').get_text())
            self.assertEqual(len(section.select('main .env-definition')), 2)
            self.assertEqual(section.select_one('html')['data-reading-mode'], 'continuous')
            self.assertIn('A statement.', section.select_one('main').get_text())
            self.assertFalse(section.select('.source-attribution'))
            self.assertNotIn('From Test source', section.select_one('main').get_text())
            entry = BeautifulSoup((root / 'tag' / global_tag('source', self.records[0]['label']) / 'index.html').read_text(), 'html.parser')
            self.assertFalse(entry.select('.source-attribution'))
            self.assertTrue(entry.select('[data-gerby-book="source"] [data-gerby-tag]'))
            check_links(root)

    def test_numerical_references_are_a_searchable_unnumbered_reader_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            navigation = self.build(root)
            route = 'numerical-references'
            page = BeautifulSoup((root / route / 'index.html').read_text(), 'html.parser')
            self.assertEqual(page.select_one('main h1').get_text(), 'Numerical references')
            self.assertEqual(sum(item['route'] == route for item in navigation), 1)
            self.assertEqual(len(json.loads((root / 'collection.json').read_text())['chapters']), 2)
            results = [item for item in json.loads((root / 'search.json').read_text())
                       if 'figure credits' in item['aliases']]
            self.assertEqual(len(results), 1)
            self.assertIn('Mario B. Schulz', results[0]['text'])
            self.assertIn('Francisco Torralbo', results[0]['text'])
            self.assertIn('Matthias Weber', results[0]['text'])
            redirect_html = (root / 'tag' / results[0]['tag'] / 'index.html').read_text()
            self.assertIn('../../numerical-references/', redirect_html)
            for link in page.select('main a[href^="#"]'):
                self.assertIsNotNone(page.find(id=link['href'][1:]), link['href'])
            check_links(root)

    def test_promoted_subject_with_no_remaining_prose_keeps_an_overview(self):
        heading = {"tag": "00000010", "label": "sec:first-part", "title": "1 First part",
                   "caption": "First part", "number": "1", "kind": "section", "section": True,
                   "topic": "Alpha", "html": '<h2 id="sec:first-part">1 First part</h2>'}
        self.records.insert(0, heading)
        self.config["section_promotions"] = {"alpha": [{
            "start": global_tag("source", heading["label"]),
            "slug": "alpha-first-part", "title": "First part"}]}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.build(root)
            overview = BeautifulSoup((root / "sections/alpha/index.html").read_text(), "html.parser")
            child = BeautifulSoup((root / "sections/alpha-first-part/index.html").read_text(), "html.parser")
            link = overview.select_one('nav[aria-label="Sections in this subject"] a')
            self.assertEqual(link["href"], "../alpha-first-part/")
            self.assertEqual(link.get_text(), "1.2 First part")
            self.assertFalse(overview.select(".env-definition"))
            self.assertEqual(len(child.select(".env-definition")), 2)
            self.assertTrue((root / "tag" / global_tag("source", heading["label"]) / "index.html").is_file())
            check_links(root)

    def test_nested_statements_and_proofs_are_readable_once(self):
        for record in self.records[:2]:
            record['html'] = record['html'].replace('<article ', f'<article id="{record["tag"]}" ')
        parent = {'tag': '00000010', 'label': 'sec:alpha', 'title': '1 Alpha', 'caption': 'Alpha', 'number': '1', 'kind': 'section', 'topic': 'Alpha', 'section': True, 'html': '<h2 id="sec:alpha">1 Alpha</h2><p>Opening explanation.</p>' + self.records[0]['html'] + '<article class="env-proof"><p>Proof. The required argument.</p></article><p>Connecting explanation.</p>' + self.records[1]['html']}
        self.records.insert(0, parent)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            illustrated_label = self.records[1]['label']
            with patch('collection.visualization', side_effect=lambda label, prefix: '<figure class="soliton-figure">A mathematical drawing.</figure>' if label == illustrated_label else ''):
                self.build(root)
            soup = BeautifulSoup((root / 'sections/alpha/index.html').read_text(), 'html.parser')
            self.assertEqual(len(soup.select('.soliton-figure')), 1)
            self.assertEqual(len(soup.select('.reading-chunk')), 1)
            self.assertEqual(len(soup.select('.env-definition')), 2)
            self.assertEqual(len(soup.select('.env-proof')), 1)
            disclosure = soup.select('.env-proof')[0].find_parent('details', class_='proof')
            self.assertIsNotNone(disclosure)
            self.assertFalse(disclosure.has_attr('open'))
            self.assertEqual(disclosure.summary.get_text(), 'Proof')
            text = soup.select_one('.section-reading').get_text()
            self.assertEqual(text.count('Opening explanation.'), 1)
            self.assertEqual(text.count('Connecting explanation.'), 1)
            ids = [node['id'] for node in soup.select('[id]')]
            self.assertEqual(len(ids), len(set(ids)))
            check_links(root)

    def test_excluded_front_matter_leaves_reading_order_and_preserves_old_urls(self):
        self.config['excluded_topics'] = ['beta']
        self.config['chapters'][0]['topics'] = ['alpha']
        self.config['entries'] = [{'tag': 'ABCDEF12', 'title': 'Removed overview', 'topic': 'beta', 'members': [{'source': 'source', 'label': self.records[2]['label']}]}]
        self.records[0]['html'] += '<p>See <a href="/tag/00000003">the overview</a>.</p>' + r'\[x=\gerbyref{00000003}{1}\]'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pages = self.build(root)
            self.assertFalse(any(p.get('section') == 'beta' for p in pages))
            chapter = BeautifulSoup((root / 'chapters/first/index.html').read_text(), 'html.parser')
            self.assertEqual([a.get_text(' ', strip=True) for a in chapter.select('main .section-list a')], ['1.1 Alpha'])
            section = BeautifulSoup((root / 'sections/alpha/index.html').read_text(), 'html.parser')
            self.assertIn('See the overview.', section.get_text())
            self.assertFalse(section.select('a[href*="ABCDEF12"]'))
            self.assertIn(r'\[x=1\]', section.get_text())
            collection = json.loads((root / 'collection.json').read_text())
            self.assertEqual({t['slug'] for t in collection['topics']}, {'alpha', 'gamma'})
            self.assertEqual(len(collection['entries']), 3)
            self.assertNotIn('ABCDEF12', {r['tag'] for r in json.loads((root / 'search.json').read_text())})
            for route in ('sections/beta', 'topics/beta', 'tag/ABCDEF12', 'books/source/tag/00000003', 'books/source/tag/ABCDEF12'):
                path = root / route / 'index.html'
                soup = BeautifulSoup(path.read_text(), 'html.parser')
                self.assertEqual((path.parent / soup.html['data-redirect'] / 'index.html').resolve(), (root / 'chapters/index.html').resolve())
                self.assertNotIn('Definition 1.1.3', soup.get_text())
            check_links(root)

    def test_section_keeps_only_the_preferred_version_of_a_shared_result(self):
        old = '<article id="22222222"><p>Definition 1. The repeated statement.</p></article><article class="env-proof"><p>Old source proof.</p></article>'
        preferred = '<article id="33333333"><p>Definition 2. The preferred statement.</p></article><article class="env-proof"><p>Preferred proof.</p></article>'
        entries = {
            'AAAAAAAA': {'tag': 'AAAAAAAA', 'topic': 'alpha', 'variants': [{'source': 'a', 'tag': '11111111', 'label': 'sec:alpha', 'title': '1 Alpha', 'caption': 'Alpha', 'number': '1', 'section': True, 'html': '<h2 id="sec:alpha">1 Alpha</h2>' + old}]},
            'BBBBBBBB': {'tag': 'BBBBBBBB', 'topic': 'alpha', 'variants': [{'source': 'b', 'tag': '33333333', 'label': 'def:new', 'title': 'Definition 2', 'html': preferred}, {'source': 'a', 'tag': '22222222', 'label': 'def:old', 'title': 'Definition 1', 'html': old}]}
        }
        html = continuous_section(list(entries.values()), entries, source_roots(entries), {'a': {'title': 'Source A'}, 'b': {'title': 'Source B'}}, {}, {}, '../../', {})
        soup = BeautifulSoup(html, 'html.parser')
        self.assertNotIn('Old source proof.', soup.get_text())
        self.assertEqual(soup.get_text().count('Preferred proof.'), 1)
        self.assertEqual(len(soup.select('.shared-entry-reference')), 1)

    def test_reading_chain_covers_every_page_once_with_reciprocal_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            order = self.build(root)
            routes = [page["route"] for page in order]
            self.assertEqual(len(routes), len(set(routes)))
            self.assertEqual(sum(route.startswith("tag/") for route in routes), 4)
            self.assertLess(routes.index("chapters/first"), routes.index("sections/alpha"))
            self.assertLess(routes.index("sections/beta"), routes.index("chapters/second"))
            for index, route in enumerate(routes):
                page = root / route / "index.html"
                soup = BeautifulSoup(page.read_text(), "html.parser")
                ids = [element['id'] for element in soup.select('[id]')]
                self.assertEqual(len(ids), len(set(ids)), route)
                for direction, offset in (("prev", -1), ("next", 1)):
                    links = soup.select(f'nav.page-navigation a[rel="{direction}"]')
                    if not 0 <= index + offset < len(routes):
                        self.assertFalse(links)
                    else:
                        self.assertEqual(len(links), 2)
                        target = (page.parent / links[0]["href"] / "index.html").resolve()
                        self.assertEqual(target, (root / routes[index + offset] / "index.html").resolve())

    def test_catalogue_example_has_one_page_number_and_search_result_with_legacy_links(self):
        examples = [self.records[0], self.records[2]]
        labels = ['ex:catalogue-round-sphere', 'ex:catalogue-round-cylinder']
        properties = []
        for record, label, title, model in zip(examples, labels, ['Alpha', 'Beta'], ['sphere', 'cylinder']):
            record.update(label=label, kind='example', caption=title, semantic_title=title)
            record['html'] = f'<article class="env-example" id="{record["tag"]}"><p><a class="environment-identifier" href="/tag/{record["tag"]}">Example <span data-tag="{record["tag"]}">9.1</span> <span class="named">({title})</span>.</a> Complete {title} statement.</p></article>'
            properties.append({**property_registry()[label], 'section': title.lower(), 'title': title, 'tag': global_tag('source', label), 'category': 'first', 'model': model, 'illustration_status': 'Exact formula'})
        heading = {'tag': '00000010', 'label': 'sec:alpha', 'kind': 'chapter', 'section': True, 'topic': 'Alpha', 'caption': 'Alpha', 'number': '9', 'title': '9 Alpha', 'html': '<h2 id="00000010">9 Alpha</h2><p>Introduction.</p>' + examples[0]['html']}
        examples[1]['html'] += '<p>See Example <a href="/tag/00000001" data-tag="00000001">9.1</a>.</p>'
        self.records = [heading, *examples, self.records[-1]]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch('collection.catalogue_properties.prepare', return_value=properties):
                order = self.build(root)
            routes = [page['route'] for page in order]
            self.assertEqual(routes[routes.index('sections/alpha') + 1], 'sections/beta')
            self.assertEqual(routes[routes.index('sections/beta') + 1], 'chapters/second')
            search = json.loads((root / 'search.json').read_text())
            for example, prop in zip(examples, properties):
                tag, topic = prop['tag'], prop['section']
                number = '1.1' if topic == 'alpha' else '1.2'
                self.assertNotIn('tag/' + tag, routes)
                page = BeautifulSoup((root / 'sections' / topic / 'index.html').read_text(), 'html.parser')
                self.assertTrue(page.h1.get_text().startswith('§ ' + number + ' '))
                self.assertFalse(page.select('.environment-identifier'))
                self.assertIn('Complete ' + prop['title'] + ' statement.', page.get_text())
                self.assertIsNotNone(page.find(id='source-' + example['tag']))
                self.assertIsNotNone(page.select_one(f'[data-gerby-tag="{example["tag"]}"]'))
                self.assertFalse(page.select('[data-gerby-tag]:not([data-section-marker])'))
                self.assertIsNotNone(page.select_one(f'[data-gerby-tag="{example["tag"]}"][data-section-marker] .tag-id'))
                legacy = BeautifulSoup((root / 'tag' / tag / 'index.html').read_text(), 'html.parser')
                self.assertEqual(legacy.html['data-redirect'], '../../sections/' + topic + '/')
                fragments = json.loads(legacy.html['data-fragments'])
                self.assertEqual(fragments['source-' + example['tag']], 'source-' + example['tag'])
                self.assertIn('case-' + example['label'].replace(':', '-') + '-1', fragments)
                matches = [r for r in search if r['tag'] == tag or tag in r['aliases']]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]['title'], number + ' ' + prop['title'])
            alpha_result = next(r for r in search if r['tag'] == properties[0]['tag'])
            self.assertIn(global_tag('source', 'sec:alpha'), alpha_result['aliases'])
            beta = BeautifulSoup((root / 'sections/beta/index.html').read_text(), 'html.parser')
            self.assertEqual(beta.select_one('a[data-tag="00000001"]').get_text(), '1.1')
            check_links(root)

    def test_a_section_named_comments_does_not_replace_the_comment_panel_anchor(self):
        self.records[-1]['topic'] = 'Comments'
        self.config['topics'][-1] = {'slug': 'comments', 'title': 'Comments'}
        self.config['chapters'][-1]['topics'] = ['comments']
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.build(root)
            soup = BeautifulSoup((root / 'chapters/second/index.html').read_text(), 'html.parser')
            self.assertEqual(len(soup.select('#comments')), 1)
            self.assertEqual(soup.select_one('#comments')['class'], ['comments-panel'])
            self.assertTrue(soup.select_one('#section-comments a'))
            check_links(root)

    def test_chapters_sections_and_subsections_expose_working_tag_routes(self):
        self.records.insert(0, {"tag": "00000010", "label": "sec:inversion", "title": "4 Inversion", "caption": "Inversion", "number": "4", "kind": "section", "topic": "Alpha", "section": True, "html": '<h2 id="sec:inversion"><span data-tag="00000010">4</span> Inversion</h2><p>Opening explanation.</p>'})
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.build(root)
            collection = json.loads((root / 'collection.json').read_text())
            for structure in [*collection['chapters'], *collection['topics']]:
                self.assertTrue((root / 'tag' / structure['tag'] / 'index.html').is_file())
            chapter = BeautifulSoup((root / 'chapters/first/index.html').read_text(), 'html.parser')
            self.assertTrue(chapter.select_one('main h1 .tag-id'))
            self.assertEqual(chapter.select_one('main .subsection-list a').get_text(), '1.1.1 Inversion')
            self.assertTrue(chapter.select_one('main .subsection-list .tag-id'))
            section = BeautifulSoup((root / 'sections/alpha/index.html').read_text(), 'html.parser')
            self.assertTrue(section.select_one('main h1 .tag-id'))
            self.assertTrue(section.select_one('.section-reading h2 .tag-id'))
            check_links(root)

    def test_labels_are_searchable_but_not_reader_headings_or_result_titles(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pages = self.build(root)
            for page in pages:
                soup = BeautifulSoup((root / page["route"] / "index.html").read_text(), "html.parser")
                self.assertNotIn("internal_label_", soup.get_text())
                self.assertNotIn("Internal label", soup.get_text())
            search = json.loads((root / "search.json").read_text())
            first = next(row for row in search if "def:internal_label_1" in row["aliases"])
            self.assertEqual(first["title"], "Definition 1.1.1")
            self.assertIn("def:internal_label_1", first["aliases"])

    def test_empty_fork_comments_are_disabled_and_identity_is_gmt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pages = self.build(root)
            for page in pages:
                soup = BeautifulSoup((root / page["route"] / "index.html").read_text(), "html.parser")
                self.assertFalse(soup.select('[data-comment-term], [data-load-comments]'))
                self.assertIn('Comments are not enabled yet.', soup.select_one('#comments').get_text())
                self.assertTrue(soup.select_one('link[rel="canonical"]')['href'].startswith('https://aosunmath.github.io/MCF-stack/'))
                self.assertEqual(soup.select_one('.brand').get_text(strip=True), TITLE)
                self.assertIn(CONTRIBUTORS, soup.select_one('#citation-text').get_text())
                self.assertIn(TITLE, soup.title.get_text())
                self.assertIn('howpublished = {' + TITLE + '}', soup.select_one('#citation-text').get_text())
                self.assertNotIn('MingchenXia/Pome', str(soup))

    def test_configured_comments_keep_stable_routes_and_github_fallback(self):
        reader = Reader({}, {}, {}, {}, {
            'enabled': True, 'repo': 'aosunmath/MCF-stack', 'repo_id': 'TEST_REPO',
            'category': 'General', 'category_id': 'TEST_CATEGORY',
            'category_slug': 'general', 'term_prefix': 'GMT Stack',
        })
        terms = []
        for route in reader.order:
            panel = BeautifulSoup(reader.comment_panel(route), 'html.parser').section
            terms.append(panel['data-comment-term'])
            self.assertEqual(panel['data-repo'], 'aosunmath/MCF-stack')
            self.assertTrue(panel['data-comment-term'].startswith('GMT Stack /'))
            self.assertIn('aosunmath/MCF-stack/discussions/new?', panel.select_one('.comment-actions a:last-child')['href'])
        self.assertEqual(len(terms), len(set(terms)))


if __name__ == "__main__":
    unittest.main()
