"""Independent mathematical and recorded-numerics checks for AIV additions."""
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'site/assets/solitons/aiv-data.json').read_text())
AUDIT=json.loads((ROOT/'site/assets/solitons/aiv-audit.json').read_text())

class AIVTests(unittest.TestCase):
    def test_axis_caps_and_monotonicity(self):
        for r in DATA['minimal']+DATA['expanders']+DATA['shrinkers']:
            with self.subTest(name=r['name']):
                points=r['points']
                self.assertEqual(points[0][0],0)
                self.assertAlmostEqual(points[0][1],r['a'],places=9)
                self.assertTrue(all(y>0 for x,y in points))
                self.assertTrue(all(b[0]>a[0] and b[1]>=a[1]-1e-10 for a,b in zip(points,points[1:])))

    def test_distinct_continuations_match_one_cone(self):
        target=DATA['shrinkers'][DATA['matched_shrinker_index']]['slope']
        self.assertEqual(len(DATA['continuations']),3)
        self.assertEqual(sum(r['swap'] for r in DATA['continuations']),1)
        for r in DATA['continuations']:
            self.assertLess(abs(r['slope']-target),1e-11)
            self.assertLess(r['diagnostics']['radius_refinement_change'],3e-9)
            self.assertLess(r['diagnostics']['ode_relative_defect'],1e-8)
        self.assertGreater(abs(DATA['continuations'][0]['a']-DATA['continuations'][1]['a']),.5)

    def test_refinements_and_dimension_eight_slope_gap(self):
        for r in AUDIT['shrinkers']:
            self.assertEqual(r['m'],r['diagnostics']['resolved_minimal_cone_crossings'])
            self.assertLess(r['diagnostics']['matching_residual'],1e-10)
            self.assertLess(r['diagnostics']['cone_slope_cutoff_change'],5e-9)
        r=next(r for r in AUDIT['expanders'] if (r['p'],r['q'],r['a'])==(2,6,.1))
        self.assertLess(r['slope']-math.sqrt(5),-2e-6)
        self.assertLess(r['diagnostics']['cone_slope_refinement_change'],1e-10)
        self.assertFalse(AUDIT['certified'])

    def test_inverse_coordinate_cone_and_linearized_eigenfunctions(self):
        # The inverse minimal equation annihilates G=z/sqrt(5); the draft's
        # interchanged coefficients would instead leave a nonzero 1/z term.
        for z in [.3,1,5]:
            G=z/math.sqrt(5);Gp=1/math.sqrt(5)
            self.assertAlmostEqual(5*Gp/z-1/G,0,places=12)
            self.assertGreater(abs(Gp/z-5/G),1)
        for k in [2,4,6]:
            for eta in [.7,1.4,3]:
                f=fp=fpp=0
                for j in range(k+1):
                    odd=math.prod(range(1,2*j+2,2))
                    c=math.comb(k,j)*(-3/5)**j/odd;n=2*j-2
                    f+=c*eta**n;fp+=c*n*eta**(n-1);fpp+=c*n*(n-1)*eta**(n-2)
                applied=5*fpp/6+(5/eta-eta/2)*fp+(.5+5/eta**2)*f
                self.assertAlmostEqual(applied,(1.5-k)*f,places=10)

    def test_existing_family_routes_are_reused(self):
        registry=json.loads((ROOT/'catalogue-visualizations.json').read_text())['entries']
        for label in ['birotational-shrinkers','birotational-expanders']:
            records=[r for r in registry if r['label']=='ex:catalogue-'+label]
            self.assertEqual(len(records),1)
            self.assertIn('CatAIV2002',records[0]['citations'])
        props=json.loads((ROOT/'catalogue-properties.json').read_text())['examples']
        r=next(r for r in props if r['label']=='ex:catalogue-aiv-eight-fattening')
        self.assertIsNone(r['cases'][0]['compact'])
        self.assertEqual(r['cases'][0]['ends']['key'],'not-recorded')

if __name__=='__main__':unittest.main()
