"""Supplementary figures remain attached to one catalogue example."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from soliton_visualizations import visualization,validate_figure

class SupplementaryFiguresTests(unittest.TestCase):
    def test_second_figure_and_alternative_drawings_are_readable_without_js(self):
        basic={'model':'limit','status':'Limit','caption':'Input','alt':'Sphere and torus'}
        second={**basic,'model':'handles','status':'Schematic','interactive':True,
                'additional_drawings':[{'model':'handles-16','title':'Genus 16 drawing'}]}
        with patch('soliton_visualizations.registry',return_value={'ex:test':{**basic,'supplementary':[second]}}):
            html=visualization('ex:test','../../')
        self.assertEqual(html.count('<figure '),2)
        self.assertIn('data-soliton="../../assets/solitons/handles.json"',html)
        self.assertIn('href="../../assets/solitons/handles-16.svg"',html)

    def test_missing_variant_asset_fails_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);assets=root/'assets/solitons';assets.mkdir(parents=True)
            (assets/'handles.svg').write_text('<svg/>')
            (assets/'handles.json').write_text(json.dumps({'vertices':[[0,0,0]],'faces':[],'paths':[],'status':'schematic'}))
            item={'model':'handles','status':'Schematic','interactive':True,
                  'additional_drawings':[{'model':'handles-16','title':'Genus 16 drawing'}]}
            with self.assertRaisesRegex(ValueError,'Missing catalogue illustration'):
                validate_figure(item,'ex:test',root)

if __name__=='__main__':unittest.main()
