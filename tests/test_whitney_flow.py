"""Independent checks of the exported Whitney flow, not an existence proof."""
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'site/assets/solitons/whitney-flow.json').read_text())
AUDIT=json.loads((ROOT/'site/assets/solitons/whitney-flow-audit.json').read_text())

class WhitneyFlowTests(unittest.TestCase):
    def test_initial_profile_matches_exact_whitney_immersion(self):
        p=DATA['frames'][0]['quarter']
        for i,(a,b) in enumerate(p):
            u=math.pi*i/(2*(len(p)-1))
            self.assertAlmostEqual(a,math.sin(u)/(1+math.cos(u)**2),places=8)
            self.assertAlmostEqual(b,math.sin(u)*math.cos(u)/(1+math.cos(u)**2),places=8)

    def test_time_normalization_and_initial_tip_velocity(self):
        frames=DATA['frames']
        self.assertEqual([f['t'] for f in frames],[i/1000 for i in range(91)])
        # At u=pi/2, gamma=(1,0), k=(-3,0), gamma^perp=(1,0).
        observed=(frames[1]['quarter'][-1][0]-1)/frames[1]['t']
        self.assertAlmostEqual(observed,-4,delta=.03)
        self.assertEqual(DATA['intrinsicDimension'],2)
        self.assertEqual(DATA['ambientDimension'],4)
        self.assertEqual(DATA['status'],'numerical-pde')

    def test_regular_snapshots_contract_and_change_shape(self):
        tips=[];heights=[];angles=[]
        for f in DATA['frames']:
            p=f['quarter']
            self.assertEqual(p[0],[0,0]);self.assertEqual(p[-1][1],0)
            self.assertTrue(all(math.isfinite(v) for q in p for v in q))
            self.assertTrue(all(a>0 and b>0 for a,b in p[1:-1]))
            self.assertTrue(all(p[i+1][0]>p[i][0] for i in range(len(p)-1)))
            tips.append(p[-1][0]);heights.append(max(q[1] for q in p))
            angles.append(math.atan2(p[1][1],p[1][0]))
        for values in [tips,heights,angles]:
            self.assertTrue(all(a>b for a,b in zip(values,values[1:])))
        self.assertGreater(tips[-1],.17)
        self.assertLess(heights[-1]/tips[-1],.5*heights[0]/tips[0])

    def test_refinement_is_disclosed_without_claiming_extinction(self):
        self.assertGreater(AUDIT['refinement_ratio'],3)
        self.assertLess(AUDIT['max_pointwise_refinement_640_1280'],3e-5)
        self.assertLess(AUDIT['max_pointwise_tolerance_change'],1e-6)
        self.assertIsNone(AUDIT['extinction_time'])
        self.assertFalse(AUDIT['singularity_included'])
        svg=(ROOT/'site/assets/solitons/whitney-flow.svg').read_text()
        self.assertIn('positive times are numerical',svg)
        self.assertNotIn('np.int',svg)
        self.assertEqual(svg.count('font-weight="600">t = '),4)

if __name__=='__main__':unittest.main()
