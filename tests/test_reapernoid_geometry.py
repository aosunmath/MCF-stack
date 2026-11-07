"""Delivered finite-start PDE data: numerical checks, not an eternal-flow proof."""
import json,math,unittest
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReapernoidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/'site/assets/solitons/reapernoid.json').read_text())
        cls.audit=json.loads((ROOT/'site/assets/solitons/reapernoid-audit.json').read_text())
    def test_default_surface_is_a_connected_annulus_with_two_display_rims(self):
        d=self.d;edges=Counter(tuple(sorted((f[k],f[(k+1)%3]))) for f in d['faces'] for k in range(3))
        self.assertEqual(set(edges.values()),{1,2});self.assertEqual(len(d['vertices'])-len(edges)+len(d['faces']),0)
        self.assertEqual(len(d['paths']),2)
        self.assertEqual({e for e,k in edges.items() if k==1},{tuple(sorted(e)) for p in d['paths'] for e in zip(p,p[1:])})
        adj=defaultdict(set)
        for a,b in edges:adj[a].add(b);adj[b].add(a)
        seen={0};todo=[0]
        while todo:
            for k in adj[todo.pop()]-seen:seen.add(k);todo.append(k)
        self.assertEqual(len(seen),len(d['vertices']))
    def test_frames_are_even_outside_the_catenoid_and_move_outward(self):
        for m in self.d['cases']:
            self.assertEqual(m['ambient'],m['n']+1)
            last=None
            for f in m['frames']:
                self.assertEqual(len(f['u']),len(m['x']))
                for r,s,w in zip(f['u'],reversed(f['u']),m['reference']):
                    self.assertTrue(math.isfinite(r));self.assertGreater(r,w-1e-7);self.assertAlmostEqual(r,s,places=7)
                if last is not None:self.assertTrue(all(b>=a-1e-7 for a,b in zip(last,f['u'])))
                last=f['u']
                # At the neck ux=0, so the radial speed is k_meridian−(n−1)/u.
                self.assertAlmostEqual(f['neck_speed'],f['meridian_tip_curvature']-(m['n']-1)/f['neck_radius'],places=7)
            zero=next(f for f in m['frames'] if f['t']==0)
            self.assertAlmostEqual(zero['neck_radius'],2,places=10)
            self.assertLess(m['simulation_start'],m['time']['min'])
    def test_refinement_offset_domain_and_time_checks_are_small_on_display_windows(self):
        for a in self.audit['cases']:
            for key in ['mesh_refinement','smaller_initial_offset','longer_domain','tighter_time_tolerance']:
                self.assertLess(max(x['max_profile_difference'] for x in a[key]),.007)
            for f in a['checkpoints']:
                self.assertGreater(f['minimum_outward_speed'],0)
                self.assertGreater(f['minimum_meridian_curvature'],0)
                self.assertGreater(f['minimum_gap_above_catenoid'],0)
                if f['temporal_residual_in_display_window'] is not None:self.assertLess(f['temporal_residual_in_display_window'],1e-5)
            self.assertGreater(a['checkpoints'][0]['meridian_tip_curvature'],a['checkpoints'][-1]['meridian_tip_curvature'])
if __name__=='__main__':unittest.main()
