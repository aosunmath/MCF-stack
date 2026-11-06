"""Independent geometric checks for illustrative assets, not existence proofs."""
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'site/assets/solitons'

def model(name):return json.loads((ASSETS/(name+'.json')).read_text())

class SolitonGeometryTests(unittest.TestCase):
    def test_round_shrinker_normalization_and_clifford_dimension(self):
        for p in model('sphere')['vertices']:
            self.assertAlmostEqual(sum(x*x for x in p),4,places=5)
        for x,y,z in model('cylinder')['vertices']:
            self.assertAlmostEqual(x*x+y*y,2,places=5)
        for p in model('clifford')['vertices']:
            self.assertEqual(len(p),4)
            self.assertAlmostEqual(p[0]**2+p[1]**2,2,places=5)
            self.assertAlmostEqual(p[2]**2+p[3]**2,2,places=5)

    def test_grim_and_catenoid_assets_match_the_stated_formulas(self):
        for name,a in [('grim-reaper',0),('tilted-grim',.65)]:
            A=1+a*a
            for x,y,z in model(name)['vertices']:
                self.assertLess(abs(z+A*math.log(math.cos(x/math.sqrt(A)))-a*y),2e-6)
        for x,y,z in model('catenoid')['vertices']:
            self.assertLess(abs(math.hypot(x,y)-math.cosh(z)),1e-6)

    def test_numerical_closure_and_source_status_are_explicit(self):
        audit=json.loads((ASSETS/'geometry-audit.json').read_text())
        self.assertLess(audit['angenent-torus']['return_angle_error'],1e-7)
        self.assertLess(audit['angenent-torus']['return_position_error'],1e-7)
        self.assertTrue(3.30<audit['angenent-torus']['outer_radius']<3.33)
        self.assertLess(audit['abresch-langer']['closure_error'],1e-7)
        for name in ['bowl','angenent-torus','abresch-langer','expanding-graph','one-sheet-expander']:
            self.assertEqual(model(name)['status'],'numerical-ode')
        # A flat quadratic graph would have f(5)=6.25, and is not the exact bowl.
        bowl=model('bowl')['vertices']
        heights=[z for x,y,z in bowl if abs(math.hypot(x,y)-5)<1e-6]
        self.assertTrue(heights)
        self.assertGreater(abs(heights[0]-6.25),1)

if __name__=='__main__':unittest.main()
