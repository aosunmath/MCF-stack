"""Checks of the delivered geometry, not a verification of nonlinear ancient MCF."""
import json,math,unittest
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'site/assets/solitons'
class CostaModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((DATA/'minimal-ancient-flows.json').read_text())
        cls.audit=json.loads((DATA/'minimal-ancient-audit.json').read_text())
    def test_connected_genus_one_mesh_has_three_open_end_cuts(self):
        d=self.d;edges=Counter(tuple(sorted((f[k],f[(k+1)%3]))) for f in d['faces'] for k in range(3))
        self.assertEqual(set(edges.values()),{1,2})
        adj=defaultdict(set)
        for a,b in edges:adj[a].add(b);adj[b].add(a)
        seen={0};todo=[0]
        while todo:
            for b in adj[todo.pop()]-seen:seen.add(b);todo.append(b)
        self.assertEqual(len(seen),len(d['vertices']))
        self.assertEqual(len(d['vertices'])-len(edges)+len(d['faces']),-3)
        self.assertEqual(len(d['paths']),3)
        boundary={e for e,n in edges.items() if n==1}
        traced={tuple(sorted(e)) for p in d['paths'] for e in zip(p,p[1:])}
        self.assertEqual(boundary,traced)
    def test_finite_unit_normals_positive_mode_and_small_offsets(self):
        d=self.d
        self.assertEqual(len(d['vertices']),len(d['normals']))
        self.assertEqual(len(d['mode']),len(d['vertices']))
        for p,n,f in zip(d['vertices'],d['normals'],d['mode']):
            self.assertTrue(all(math.isfinite(x) for x in p+n))
            self.assertAlmostEqual(sum(x*x for x in n),1,places=7)
            self.assertGreaterEqual(f,0)
        self.assertAlmostEqual(max(d['mode']),1)
        self.assertLess(3*d['amplitude']*self.audit['max_principal_curvature'],.6)
    def test_truncated_mode_has_small_equation_residual_and_recorded_sensitivity(self):
        a=self.audit
        for item in [a,*a['refinement'],*a['domain_comparison']]:
            self.assertLess(item['relative_eigen_residual'],1e-9)
            self.assertGreater(item['minimum_interior_mode'],0)
        self.assertLess(abs(a['eigenvalue']-a['refinement'][1]['eigenvalue']),.001)
        self.assertGreater(a['domain_comparison'][1]['eigenvalue'],a['domain_comparison'][0]['eigenvalue'])
if __name__=='__main__':unittest.main()
