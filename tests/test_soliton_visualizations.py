"""Supplementary figures remain attached to one catalogue example."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from soliton_visualizations import visualization,validate_figure,validate_visualizations

class SupplementaryFiguresTests(unittest.TestCase):
    def test_experiment_keeps_static_drawing_and_a_full_page_link(self):
        item={'model':'limit','status':'Schematic','caption':'Input','alt':'Torus',
              'experiment':{'path':'visualizations/flow/index.html',
                            'title':'Flow & candidate','caption':'Numerical evidence only.'}}
        with patch('soliton_visualizations.registry',return_value={'ex:test':item}):
            html=visualization('ex:test','../../')
        self.assertIn('src="../../assets/solitons/limit.svg"',html)
        self.assertIn('href="../../visualizations/flow/index.html"',html)
        self.assertIn('src="../../visualizations/flow/index.html"',html)
        self.assertIn('sandbox="allow-scripts"',html)
        self.assertIn('title="Flow &amp; candidate"',html)
        self.assertIn('Numerical evidence only.',html)

    def test_additional_experiment_preserves_original_anchor_and_both_viewers(self):
        first={'path':'visualizations/first/index.html','title':'First flow','caption':'First experiment.'}
        second={'id':'second-mode','path':'visualizations/second/index.html',
                'title':'Second flow','caption':'No convergence claim.'}
        item={'model':'limit','status':'Schematic','caption':'Input','alt':'Torus',
              'experiment':first,'additional_experiments':[second]}
        with patch('soliton_visualizations.registry',return_value={'ex:test':item}):
            html=visualization('ex:test','../../')
        self.assertEqual(html.count('<iframe '),2)
        self.assertEqual(html.count('id="experiment-limit"'),1)
        self.assertEqual(html.count('id="experiment-second-mode"'),1)
        for path in (first['path'],second['path']):
            self.assertIn('href="../../'+path+'"',html)
            self.assertIn('src="../../'+path+'"',html)
        self.assertIn('No convergence claim.',html)

    def test_additional_experiment_requires_its_own_page_and_unique_anchor(self):
        entries={'tag':{'variants':[{'source':'gmt-foundations','label':'ex:test'}]}}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'assets/solitons').mkdir(parents=True)
            (root/'assets/solitons/limit.svg').write_text('<svg/>')
            (root/'first.html').write_text('<html></html>')
            second={'id':'second','path':'second.html'}
            item={'model':'limit','category':'shrinkers','experiment':{'path':'first.html'},
                  'additional_experiments':[second]}
            with patch('soliton_visualizations.registry',return_value={'ex:test':item}):
                with self.assertRaisesRegex(ValueError,'Missing numerical experiment'):
                    validate_visualizations(entries,root)
                (root/'second.html').write_text('<html></html>')
                validate_visualizations(entries,root)
                for anchor in ('limit','bad anchor','../outside'):
                    second['id']=anchor
                    with self.assertRaisesRegex(ValueError,'Invalid or repeated numerical experiment anchor'):
                        validate_visualizations(entries,root)

    def test_experiment_requires_an_existing_local_html_page(self):
        entries={'tag':{'variants':[{'source':'gmt-foundations','label':'ex:test'}]}}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'assets/solitons').mkdir(parents=True)
            (root/'assets/solitons/limit.svg').write_text('<svg/>')
            item={'model':'limit','category':'shrinkers','experiment':{'path':'visualizations/flow/index.html'}}
            with patch('soliton_visualizations.registry',return_value={'ex:test':item}):
                with self.assertRaisesRegex(ValueError,'Missing numerical experiment'):
                    validate_visualizations(entries,root)
                page=root/item['experiment']['path']
                page.parent.mkdir(parents=True)
                page.write_text('<html></html>')
                validate_visualizations(entries,root)
                for path in ('../flow.html','/flow.html','visualizations/flow.json'):
                    item['experiment']['path']=path
                    with self.assertRaisesRegex(ValueError,'Invalid numerical experiment path'):
                        validate_visualizations(entries,root)

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
