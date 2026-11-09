"""Check published numerical data without requiring SciPy in the website build."""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class LeeTsaiFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'site/assets/solitons/lee-tsai.json').read_text())

    def test_initial_boundary_monotonicity_and_concavity(self):
        x=self.data['x']
        self.assertEqual(len(x),301)
        initial=self.data['frames'][0]['u']
        for a,b in zip(x,initial):
            self.assertAlmostEqual(b,.06*(1-a*a),delta=1e-6)
        for f in self.data['frames']:
            u=f['u']
            self.assertEqual(u[0],0)
            self.assertEqual(u[-1],0)
            self.assertGreater(min(u[1:-1]),0)
            slopes=[(b-a)/(y-z) for a,b,z,y in zip(u,u[1:],x,x[1:])]
            self.assertLess(max(b-a for a,b in zip(slopes,slopes[1:])),2e-6)
        for a,b in zip(self.data['frames'],self.data['frames'][1:]):
            self.assertLessEqual(max(v-u for u,v in zip(a['u'],b['u'])),1e-10)

    def test_refinement_and_positive_necks(self):
        a=self.data['audit']
        self.assertEqual(a['mesh_points'],[601,1201,2401])
        self.assertLess(a['medium_to_fine']['max_absolute_height_difference'],1e-6)
        self.assertLess(a['medium_to_fine']['max_relative_to_frame_height'],.0002)
        self.assertLess(a['time_tolerance_refinement']['max_absolute_height_difference'],2e-9)
        for f in self.data['frames']:
            self.assertGreater(min(f['neckRadii']),0)
            self.assertAlmostEqual(*f['neckRadii'],delta=1e-8)
        self.assertLess(self.data['frames'][-1]['neckRadii'][0],self.data['frames'][0]['neckRadii'][0]/4)

if __name__=='__main__':unittest.main()
