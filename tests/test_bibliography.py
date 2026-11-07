from pathlib import Path
import sys
import unittest

from bs4 import BeautifulSoup
from pybtex.database.input.bibtex import Parser
from pybtex.plugin import find_plugin

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapters"))
from common import bibliography_entry_for_html, bibliography_sort_key


class BibliographyTests(unittest.TestCase):
    def test_author_order_uses_surnames_coauthors_year_and_tex_accents(self):
        database = Parser().parse_string(r"""
@misc{last, author={Zebra, Alice}, title={First title}, year={1990}}
@misc{early, author={Abresch, Uwe and Langer, Joel}, title={Z title}, year={1986}}
@misc{coauthor, author={Abresch, Uwe and Zebra, Alice}, title={A title}, year={1980}}
@misc{later, author={Abresch, Uwe and Langer, Joel}, title={A title}, year={2000}}
@misc{title, author={Abresch, Uwe and Langer, Joel}, title={A title}, year={1986}}
@misc{accent, author={M{\o}ller, Niels Martin}, title={A title}, year={2014}}
@misc{next, author={Moser, Jürgen}, title={A title}, year={2000}}
@book{editor, editor={Brakke, Kenneth}, title={A book}, year={1978}}
""")
        ordered = sorted(database.entries, key=lambda key: bibliography_sort_key(database.entries[key]))
        self.assertEqual(ordered, ['title', 'early', 'later', 'coauthor', 'editor', 'accent', 'next', 'last'])

    def test_sorting_preserves_suffixes_and_falls_back_to_organization_or_title(self):
        database = Parser().parse_string(r"""
@misc{suffix, author={Minicozzi, II, William P.}, title={A title}, year={2012}}
@misc{organization, organization={Zürich Institute}, title={A report}}
@misc{anonymous, title={Évolution}}
""")
        self.assertEqual(bibliography_sort_key(database.entries['suffix'])[0], 'minicozzi  william p.  ii')
        self.assertEqual(bibliography_sort_key(database.entries['organization'])[0], 'zurich institute')
        self.assertEqual(bibliography_sort_key(database.entries['anonymous'])[0], 'evolution')

    def test_tex_publication_link_renders_as_a_real_link_without_changing_source(self):
        database = Parser().parse_string(r"""
@misc{book, author={Jean-Pierre Demailly}, year={2012},
 title={Complex Analytic and Differential Geometry},
 howpublished={\href{https://example.org/~author/book.pdf}{Author's website}}}
@article{paper, author={An Author}, title={A paper}, year={2000},
 journal={A journal}, volume={1}, pages={1--2}}
""")
        style = find_plugin("pybtex.style.formatting", "plain")()
        backend = find_plugin("pybtex.backends", "html")()

        def render(entry):
            return next(iter(style.format_entries([entry]))).text.render(backend)

        original = database.entries["book"]
        converted = bibliography_entry_for_html(original)
        soup = BeautifulSoup(render(converted), "html.parser")
        self.assertEqual(soup.a["href"], "https://example.org/~author/book.pdf")
        self.assertIn("Author's website", soup.get_text())
        self.assertNotIn(r"\href", soup.get_text())
        self.assertNotIn("url", original.fields)
        self.assertEqual(converted.fields["title"], original.fields["title"])
        self.assertEqual(converted.persons, original.persons)
        self.assertEqual(converted.fields["year"], original.fields["year"])
        paper = database.entries["paper"]
        self.assertEqual(render(bibliography_entry_for_html(paper)), render(paper))
