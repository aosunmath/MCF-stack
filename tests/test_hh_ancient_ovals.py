import json
import math
from collections import Counter
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'site/assets/solitons/hh-ancient-ovals.json').read_text())

class HHAncientOvalTests(unittest.TestCase):
    def test_time_normalization_symmetry_convexity_and_contraction(self):
        frames=DATA['frames']
        self.assertEqual(len(frames),121)
        self.assertEqual(frames[0]['time'],-1000)
        self.assertAlmostEqual(frames[-1]['time'],-.001)
        self.assertAlmostEqual(frames[60]['aspect'],2,places=7)
        self.assertGreater(frames[0]['aspect'],3.8)
        self.assertLess(frames[-1]['aspect'],1.05)
        previous=(math.inf,math.inf)
        for f in frames:
            p=f['profile'];middle=len(p)//2
            self.assertEqual(p[0][1],0);self.assertEqual(p[-1][1],0)
            self.assertEqual(p[middle][0],0)
            self.assertTrue(all(r>0 for x,r in p[1:-1]))
            self.assertTrue(all(a[0]>b[0] for a,b in zip(p,p[1:])))
            for (x,r),(xx,rr) in zip(p,reversed(p)):
                self.assertAlmostEqual(x,-xx,places=7);self.assertAlmostEqual(r,rr,places=7)
            # The upper meridian is concave as a graph r(x).
            slopes=[(b[1]-a[1])/(b[0]-a[0]) for a,b in zip(p,p[1:])]
            self.assertTrue(all(b>a for a,b in zip(slopes,slopes[1:])))
            physical=(p[0][0]*math.sqrt(-f['time']),p[middle][1]*math.sqrt(-f['time']))
            self.assertTrue(all(a<b for a,b in zip(physical,previous)))
            previous=physical

    def test_mesh_is_closed_orientable_and_has_spherical_euler_characteristic(self):
        edges=Counter();orientation=Counter()
        for face in DATA['faces']:
            self.assertEqual(len(set(face)),3)
            for a,b in zip(face,face[1:]+face[:1]):
                edge=tuple(sorted((a,b)));edges[edge]+=1;orientation[edge]+=1 if a<b else -1
        self.assertEqual(set(edges.values()),{2})
        self.assertEqual(set(orientation.values()),{0})
        self.assertEqual(len(DATA['vertices'])-len(edges)+len(DATA['faces']),2)

    def test_comparison_results_and_source_limitations_are_retained(self):
        audit=DATA['audit']
        self.assertEqual(DATA['status'],'numerical-pde')
        self.assertGreater(audit['minimum_rescaled_principal_radius'],0)
        self.assertEqual(audit['normalized_sphere_rhs_error'],0)
        self.assertLess(audit['grid_refinement_max_support_difference'],.003)
        self.assertLess(audit['seed_length_max_support_difference'],1e-6)
        self.assertLess(audit['time_tolerance_max_support_difference'],1e-6)
        self.assertIn('not rigorous',audit['interpretation'])
        # Unit H at a bowl tip means f(r)/r^2 tends to 1/4, not 1/2.
        x,r=DATA['bowl_profile'][3]
        self.assertAlmostEqual(-x/r**2,.25,delta=.001)
        self.assertTrue(all(x<=0 and r>=0 for x,r in DATA['bowl_profile']))

if __name__=='__main__':unittest.main()
