import json
from pathlib import Path
import sys
import tempfile
import unittest

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collection import prepare_fragment, check_links
from numbering import assign_numbers
from reader import Reader, display_title
from structure import arrange_sections, title_key


class NumberingTests(unittest.TestCase):
    def setUp(self):
        self.entries = {}
        for index, (kind, caption, old) in enumerate((("chapter", "Analysis", "47"), ("section", "Inversion", "4"), ("theorem", "Kelvin transform", "4.1"), ("equation", "", "2"), ("lemma", "", "4.2"), ("section", "Boundary limits", "5"), ("theorem", "", "5.1")), 1):
            tag = f"{index:08X}"
            variant = {"source": "first", "tag": tag, "label": "label:" + tag, "kind": kind, "caption": caption, "number": old, "title": old + " " + caption, "section": kind in {"chapter", "section"}, "html": ""}
            self.entries[tag] = {"tag": tag, "topic": "analysis", "kind": kind, "variants": [variant], "components": []}
        self.topics = {"analysis": {"title": "Analysis"}}
        self.config = {"chapters": [{"slug": "analysis", "number": 3, "title": "Analysis", "topics": ["analysis"]}], "section_promotions": {"analysis": [{"start": "00000002", "slug": "inversion", "title": "Inversion"}, {"start": "00000006", "slug": "limits", "title": "Boundary limits"}]}}

    def arrange(self):
        config = arrange_sections(self.entries, self.topics, self.config)
        return config, assign_numbers({c["slug"]: c for c in config["chapters"]}, self.entries)

    def test_numbers_follow_current_section_and_reset_after_a_split(self):
        _, numbers = self.arrange()
        self.assertEqual(display_title(self.entries["00000003"]), "Theorem 3.2.1 (Kelvin transform)")
        self.assertEqual(display_title(self.entries["00000004"]), "Equation 3.2.2")
        self.assertEqual(display_title(self.entries["00000005"]), "Lemma 3.2.3")
        self.assertEqual(display_title(self.entries["00000007"]), "Theorem 3.3.1")
        self.assertEqual(numbers["first", "00000002"]["number"], "3.2")
        # Source coordinates remain provenance, never the reading locator.
        self.assertEqual(self.entries["00000003"]["variants"][0]["number"], "4.1")

    def test_merged_source_variants_share_one_number(self):
        variant = {**self.entries["00000003"]["variants"][0], "source": "second", "number": "99.7"}
        self.entries["00000003"]["variants"].append(variant)
        _, numbers = self.arrange()
        self.assertEqual(numbers["second", variant["tag"]]["number"], "3.2.1")

    def test_section_example_uses_section_number_without_consuming_a_subordinate_number(self):
        config, _ = self.arrange()
        primary = self.entries['00000003']
        primary.update(section_example=True, section_title='Inversion')
        numbers = assign_numbers({c['slug']: c for c in config['chapters']}, self.entries)
        self.assertEqual(primary['number'], '3.2')
        self.assertEqual(display_title(primary), '3.2 Inversion')
        self.assertEqual(self.entries['00000004']['number'], '3.2.1')
        self.assertEqual(numbers['first', primary['variants'][0]['label']]['number'], '3.2')
        self.assertEqual(primary['variants'][0]['number'], '4.1')
        # A different descriptive caption survives without a second locator.
        variant = {**primary['variants'][0], 'html': '<article id="00000003"><p><a class="environment-identifier" href="/tag/00000003">Theorem <span data-tag="00000003">4.1</span> <span class="named">(Kelvin transform)</span>.</a> Complete statement.</p></article>'}
        rendered = prepare_fragment(variant, {('first', '00000003'): '00000003'}, {}, '../../', numbering=numbers)
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertIn('(Kelvin transform)', soup.get_text())
        self.assertIn('Complete statement.', soup.get_text())
        self.assertFalse(soup.select('.environment-identifier'))
        self.assertIsNotNone(soup.find(id='first-00000003'))

    def test_descendant_of_a_merged_clause_follows_its_canonical_statement(self):
        parent = self.entries['00000003']
        parent['components'] = [{'source': 'second', 'label': 'condition', 'tag': '000000AA', 'number': 'i'}]
        equation = self.entries['00000004']
        equation['topic'] = 'old-source-section'
        equation['variants'][0].update(source='second', parent_label='condition')
        self.topics['old-source-section'] = {'title': 'Old source section'}
        _, numbers = self.arrange()
        self.assertEqual(equation['topic'], parent['topic'])
        self.assertEqual(equation['number'].rsplit('.', 1)[0], parent['number'].rsplit('.', 1)[0])
        self.assertEqual(numbers['second', '00000004']['number'], equation['number'])
        order = list(self.entries)
        self.assertEqual(order.index(equation['tag']), order.index(parent['tag']) + 1)

    def test_logical_clauses_keep_tags_but_share_the_statement_badge(self):
        clause = {"source": "first", "tag": "00000009", "label": "item:condition", "number": "1"}
        self.entries["00000003"]["components"] = [clause]
        _, numbers = self.arrange()
        variant = {**self.entries["00000003"]["variants"][0], "html": '<article id="00000003"><ol><li id="00000009">A condition.</li></ol></article>'}
        result = prepare_fragment(variant, {}, {}, '../../', numbering=numbers)
        soup = BeautifulSoup(result, 'html.parser')
        self.assertTrue(soup.find(id='first-00000009'))
        self.assertFalse(soup.select('[data-gerby-tag="00000009"]'))
        self.assertTrue(soup.select('[data-gerby-tag="00000003"]'))
        self.assertTrue(soup.find(id='first-00000009').select_one('.tag-id'))

    def test_html_and_math_references_change_without_touching_mathematics(self):
        _, numbers = self.arrange()
        variant = {**self.entries["00000003"]["variants"][0], "html": '<a class="environment-identifier" href="/tag/00000003">Theorem <span data-tag="00000003">4.1</span>.</a><p>By (<a href="/tag/00000004" data-tag="00000004">2</a>), $d=2$.</p>' + r'\[x=2\quad\text{by \gerbyref{00000003}{4.1}}\]'}
        links = {("first", tag): tag for tag in self.entries}
        html = prepare_fragment(variant, links, {}, "../../", numbering=numbers)
        self.assertIn('data-tag="00000003">3.2.1</span>', html)
        self.assertIn('data-tag="00000004" href="../../tag/00000004/">3.2.2</a>', html)
        self.assertIn(r"\href{../../tag/00000003/}{3.2.1}", html)
        self.assertIn("$d=2$", html)
        self.assertIn("x=2", html)

    def test_imported_headings_appear_in_chapter_subsection_lists(self):
        config = arrange_sections(self.entries, self.topics, {**self.config, "section_promotions": {}})
        reader = Reader({c["slug"]: c for c in config["chapters"]}, self.topics, self.entries, {}, {})
        soup = BeautifulSoup(reader.section_list("analysis", "../../", subsections=True), "html.parser")
        self.assertEqual([a.get_text() for a in soup.select('.subsection-list a')], ['3.1.1 Inversion', '3.1.5 Boundary limits'])
        self.assertNotIn("tag/00000001", str(soup))
        self.assertNotIn("tag/00000001", reader.pages)

    def test_a_second_source_introduction_returns_to_the_overview(self):
        second = {**self.entries["00000001"], "tag": "00000008"}
        self.entries[second["tag"]] = second
        self.arrange()
        self.assertEqual(second["topic"], "analysis")
        self.assertTrue(second["section_intro"])

    def test_missing_split_boundaries_fail_instead_of_silently_moving_content(self):
        self.config["section_promotions"]["analysis"][0]["start"] = "DEADBEEF"
        with self.assertRaisesRegex(ValueError, "Missing or reordered"):
            self.arrange()

    def test_a_promoted_heading_is_absorbed_even_with_an_editorial_title(self):
        self.config["section_promotions"]["analysis"][0]["title"] = "Inversion and Kelvin transforms"
        self.arrange()
        self.assertTrue(self.entries["00000002"]["section_intro"])
        self.assertEqual(self.entries["00000003"]["number"], "3.2.1")

    def test_tex_styling_does_not_hide_a_duplicate_section_title(self):
        self.assertEqual(title_key(r"Multiplier-ideal envelopes and $\mathcal I$-goodness"), title_key("Multiplier-ideal envelopes and I-goodness"))

    def test_build_check_rejects_stale_display_numbers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sources/first").mkdir(parents=True)
            (root / "collection.json").write_text(json.dumps({"entries": [{"tag": "AAAAAAAA", "number": "3.2.1"}]}))
            (root / "sources/first/tags.json").write_text(json.dumps([{"tag": "00000003", "canonical_tag": "AAAAAAAA"}]))
            page = root / "index.html"
            page.write_text('<div data-gerby-book="first"><span data-tag="00000003">4.1</span></div>')
            with self.assertRaisesRegex(ValueError, "Stale source numbering"):
                check_links(root)
            page.write_text(page.read_text().replace('>4.1<', '>3.2.1<'))
            check_links(root)

    def test_equation_labels_have_a_shared_row_and_align_rows_get_current_tags(self):
        _, numbers = self.arrange()
        variant = {**self.entries["00000004"]["variants"][0], "html": '<div class="equation"><span class="equation-label"><a href="/tag/00000004" data-tag="00000004">2</a></span><div>\\[x=2\\]</div></div>'}
        html = prepare_fragment(variant, {("first", "00000004"): "00000004"}, {}, "../../", numbering=numbers)
        self.assertIn('class="equation numbered-equation"', html)
        numbers["first", "row"] = {"math_row": True, "tag": "00000004", "number": "3.2.2"}
        variant["html"] = r'\begin{align}x=2\label{row}\end{align}'
        self.assertIn(r"\tag{3.2.2}", prepare_fragment(variant, {}, {}, "../../", numbering=numbers))

    def test_multirow_equations_number_the_first_row_without_an_external_duplicate(self):
        template = self.entries["00000004"]["variants"][0]
        rows = {}
        for tag, label, is_row in (("00000004", "eq:first", False), ("00000008", "eq:second", True), ("00000009", "eq:third", True)):
            variant = {**template, "tag": tag, "label": label, "math_row": is_row}
            rows[tag] = {"tag": tag, "topic": "analysis", "kind": "equation", "variants": [variant], "components": []}
        numbers = assign_numbers({"analysis": {"number": 3, "topics": ["analysis"]}}, rows)
        links = {("first", tag): tag for tag in rows}
        for environment in ("align", "align*", "gather", "gather*", "eqnarray", "eqnarray*"):
            with self.subTest(environment=environment):
                separator = "=" if environment.startswith("gather") else "&=&" if environment.startswith("eqnarray") else "&="
                equations = [variable + separator + str(index) + r"\label{" + label + "}"
                             for index, (variable, label) in enumerate(zip(("x", "y", "z"), ("eq:first", "eq:second", "eq:third")), 1)]
                body = r"\begin{" + environment + "}" + r"\\".join(equations) + r"\end{" + environment + "}"
                variant = {**rows["00000004"]["variants"][0], "html": '<div class="equation" id="00000004"><span class="equation-label"><a href="/tag/00000004" data-tag="00000004">2</a></span><div>' + body + '</div></div>'}
                rendered = prepare_fragment(variant, links, {}, "../../", numbering=numbers)
                soup = BeautifulSoup(rendered, "html.parser")
                wrapper = soup.find(id="first-00000004")
                self.assertIsNotNone(wrapper)
                self.assertFalse(soup.select(".equation-label"))
                self.assertEqual(len(wrapper.select('[data-gerby-tag="00000004"]')), 1)
                self.assertEqual(wrapper.select_one('[data-gerby-tag="00000004"] .tag-id').get_text(), "00000004")
                for tag in rows:
                    self.assertEqual(rendered.count(r"\tag{" + numbers["first", tag]["number"] + "}"), 1)
                self.assertNotIn(r"\label{", rendered)
                for index, variable in enumerate(("x", "y", "z"), 1):
                    self.assertIn(variable + separator + str(index), soup.get_text())

    def test_standalone_array_row_keeps_its_html_label_and_permanent_marker(self):
        self.entries["00000004"]["variants"][0]["math_row"] = True
        _, numbers = self.arrange()
        variant = {**self.entries["00000004"]["variants"][0], "html": '<div class="equation" id="00000004"><span class="equation-label"><a href="/tag/00000004" data-tag="00000004">2</a></span><div>' + r'\[\begin{aligned}x&=2\label{label:00000004}\end{aligned}\]' + '</div></div>'}
        rendered = prepare_fragment(variant, {("first", "00000004"): "00000004"}, {}, "../../", numbering=numbers)
        soup = BeautifulSoup(rendered, "html.parser")
        wrapper = soup.find(id="first-00000004")
        self.assertIsNotNone(wrapper)
        self.assertEqual(len(wrapper.select(".equation-label")), 1)
        label = wrapper.select_one('.equation-label a[data-tag="00000004"]')
        self.assertEqual(label.get_text(), numbers["first", "00000004"]["number"])
        self.assertEqual(label["href"], "../../tag/00000004/")
        self.assertEqual(len(wrapper.select('[data-gerby-tag="00000004"]')), 1)
        self.assertIn(r"\begin{aligned}x&=2\end{aligned}", soup.get_text())
        self.assertNotIn(r"\tag{", rendered)
        self.assertNotIn(r"\label{", rendered)


if __name__ == "__main__":
    unittest.main()
