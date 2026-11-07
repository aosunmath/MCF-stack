"""Check geometric invariants of the exported finite-start numerical flow."""
import json
import math
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class ReaperFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'site/assets/solitons/grim-reaper-chains.json').read_text())
        cls.audit=json.loads((ROOT/'site/assets/solitons/grim-reaper-chains-audit.json').read_text())

    def test_connected_graph_and_fixed_outer_ends(self):
        frames=self.data['frames']
        self.assertEqual(len(frames),151)
        self.assertEqual([frames[0]['t'],frames[-1]['t']],[-6,9])
        self.assertEqual(self.data['paths'],[list(range(901))])
        for frame in frames:
            pts=frame['points']
            self.assertEqual(len(pts),901)
            self.assertTrue(all(math.isfinite(v) for p in pts for v in p))
            self.assertEqual(pts[0][0],-32)
            self.assertEqual(pts[-1][0],-32)
            self.assertLess(max(a[1]-b[1] for a,b in zip(pts,pts[1:])),2e-6)
            for a,b in zip(pts,reversed(pts)):
                self.assertAlmostEqual(a[0],b[0],places=5)
                self.assertAlmostEqual(a[1]+b[1],3*math.pi,places=5)

    def test_past_tips_follow_reapers_and_the_flow_changes_shape(self):
        past=self.data['frames'][0]['points']
        center=past[450]
        self.assertAlmostEqual(center[0],-6,delta=.02)
        self.assertAlmostEqual(max(x for x,y in past),6,delta=.02)
        late=self.data['frames'][-1]['points']
        self.assertLess(max(x for x,y in late),-1)
        self.assertAlmostEqual(late[450][0],max(x for x,y in late),places=5)

    def test_numerical_diagnostics(self):
        self.assertLess(self.audit['space_and_time_refinement'],.01)
        self.assertLess(self.audit['earlier_start'],.005)
        self.assertLess(self.audit['farther_endpoints'],.001)
        self.assertLess(self.audit['single_reaper_translation_error'],.004)
        self.assertLess(abs(self.audit['signed_area_balance_error']),.05)
        self.assertLess(self.audit['reflection_symmetry_error'],1e-8)

if __name__=='__main__':unittest.main()
