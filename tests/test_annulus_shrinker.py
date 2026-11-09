"""Independent checks of the numerical annulus data and conserved quantity."""
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AnnulusShrinkerTests(unittest.TestCase):
    def test_phase_period_and_geometric_invariant(self):
        data = json.loads((ROOT/'site/assets/solitons/halldorsson-dense.json').read_text())
        for v in data['variants']:
            self.assertLess(abs(v['alpha']-v['target']), 1e-10)
            self.assertTrue(.5 < v['target'] < 1/math.sqrt(2))
            constant = v['curvature'][0]*math.exp(-v['r_min']**2/4)
            radii = [math.hypot(*p) for p in v['base']]
            for k, r in zip(v['curvature'], radii):
                self.assertLess(abs(k*math.exp(-r*r/4)-constant), 1e-10)
            self.assertAlmostEqual(min(radii), v['r_min'], places=9)
            self.assertAlmostEqual(max(radii), v['r_max'], places=9)
            for diagnostic in v['diagnostics'].values():
                self.assertLess(diagnostic, 1e-8)
            self.assertAlmostEqual(v['theta'][-1], 2*math.pi*v['alpha'], places=10)


if __name__ == '__main__':
    unittest.main()
