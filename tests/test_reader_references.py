from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from collection import prepare_fragment
from reader_references import page_references, bibliography, source_catalogue


class ReaderReferenceTests(unittest.TestCase):
    def setUp(self):
        self.refs = {'R1': {'html': 'A. Author. <em>First source</em>. 2001.', 'sources': [{'source': 'book', 'key': 'Author01'}]}}

    def test_citations_keep_unique_return_links_including_inside_closed_proofs(self):
        fragment = '<p><a data-reference="R1">Author01</a></p><details class="proof"><summary>Proof</summary><p><a data-reference="R1">Author01</a></p></details>'
        html, used = page_references(fragment, self.refs, '../../')
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(used, ['R1'])
        citations = soup.select('a[data-reference]')
        self.assertEqual([a['id'] for a in citations], ['cite-R1-1', 'cite-R1-2'])
        self.assertEqual({a['href'] for a in citations}, {'#reference-R1'})
        self.assertEqual(len(soup.select('#reference-R1')), 1)
        self.assertFalse(soup.select_one('details.proof').has_attr('open'))
        self.assertIsNotNone(soup.select_one('a[href="#cite-R1-2"]'))
        self.assertIsNotNone(soup.select_one('a[href="../../references/#R1"]'))

    def test_bibliography_returns_to_exact_local_reference(self):
        soup = BeautifulSoup(bibliography(self.refs, {'R1': {'sections/example': 'Example section', 'tag/ABC': 'A theorem'}}), 'html.parser')
        self.assertEqual(soup.select_one('#R1 h2').get_text(), '[Author01]')
        self.assertEqual([a['href'] for a in soup.select('#R1 a')], ['../sections/example/#reference-R1', '../tag/ABC/#reference-R1'])

    def test_bibliography_uses_author_sort_metadata_instead_of_display_names_or_keys(self):
        refs = {
            'RZ': {'html': 'Alice Zebra. <em>A paper</em>. 1990.', 'sort_key': ['zebra  alice', '1990', 'a paper'], 'sources': [{'source': 'book', 'key': 'A1990'}]},
            'RA': {'html': 'Uwe Abresch. <em>Z paper</em>. 1986.', 'sort_key': ['abresch  uwe', '1986', 'z paper'], 'sources': [{'source': 'book', 'key': 'Z1986'}]},
        }
        soup = BeautifulSoup(bibliography(refs, {'RA': {'sections/example': 'Example'}}), 'html.parser')
        self.assertEqual([entry['id'] for entry in soup.select('.bibliography-entry')], ['RA', 'RZ'])
        self.assertEqual(soup.select_one('#RA h2').get_text(), '[Z1986]')
        self.assertEqual(soup.select_one('#RA a')['href'], '../sections/example/#reference-RA')

    def test_proof_wrapping_preserves_equation_anchors_and_never_hides_statement(self):
        variant={'source':'book','label':'prop:test','tag':'ABCD1234','html':'<article class="env-proposition">Statement.</article><article class="env-proof"><p><strong>Proof.</strong> Argument <a href="#equation">below</a>.</p><div id="equation">x=y</div></article>'}
        soup=BeautifulSoup(prepare_fragment(variant,{}, {}, '../../'),'html.parser')
        self.assertIsNone(soup.select_one('.env-proposition').find_parent('details'))
        proof=soup.select_one('details.proof')
        self.assertFalse(proof.has_attr('open'))
        self.assertIsNotNone(proof.select_one('#book-equation'))
        self.assertEqual(proof.a['href'],'#book-equation')
        self.assertEqual(len(proof.select('.env-proof')),1)

    def test_catalogue_does_not_promote_unreviewed_files_to_cited_sources(self):
        items={'files':[{'filename':'first.pdf','title':'Checked work','bibliography_key':'Author01'}, {'filename':'second.pdf','title':'Unreviewed work','bibliography_key':None}]}
        soup=BeautifulSoup(source_catalogue(items,'book',{('book','Author01'):'R1'},'../../'),'html.parser')
        self.assertEqual(len(soup.select('a')),1)
        self.assertIn('Catalogued for further study (1 files)',soup.get_text())
        self.assertIn('Unreviewed work',soup.get_text())
