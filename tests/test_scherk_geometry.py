"""Check the displayed patch topology and numerical provenance, not PDE existence."""
import collections
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class ScherkGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'site/assets/solitons/scherk-translators.json').read_text())

    def test_fundamental_patch_is_a_disk_with_expected_boundary(self):
        d=self.data;v=d['vertices'];f=d['faces']
        self.assertTrue(all(len(p)==3 and all(math.isfinite(x) for x in p) for p in v))
        edges=collections.Counter(tuple(sorted((face[i],face[(i+1)%3]))) for face in f for i in range(3))
        self.assertEqual(set(edges.values()),{1,2})
        self.assertEqual(len(v)-len(edges)+len(f),1)
        graph=collections.defaultdict(set);boundary=collections.defaultdict(set)
        for (a,b),count in edges.items():
            graph[a].add(b);graph[b].add(a)
            if count==1:
                boundary[a].add(b);boundary[b].add(a)
                p,q=v[a],v[b]
                on_cap=abs(abs(p[2])-1.5)<1e-6 and abs(p[2]-q[2])<1e-6
                on_axis=all(abs(abs(r[0])-d['length']/2)<1e-6 and abs(abs(r[1])-d['width']/2)<1e-6 for r in [p,q]) and all(abs(p[i]-q[i])<1e-6 for i in [0,1])
                self.assertTrue(on_cap or on_axis)
        self.assertTrue(all(len(neighbors)==2 for neighbors in boundary.values()))
        seen={0};todo=[0]
        while todo:
            for j in graph[todo.pop()]-seen:seen.add(j);todo.append(j)
        self.assertEqual(len(seen),len(v))

    def test_finite_problem_and_refinement_are_labeled(self):
        d=self.data;a=d['audit'];self.assertIn('corner',d['status'])
        self.assertAlmostEqual(d['width'],math.pi/2)
        self.assertGreater(d['length'],d['width'])
        self.assertEqual(d['boundaryHeight'],2.5)
        for item in a.values():
            self.assertLess(item['stencil_residual_max'],1e-7)
            self.assertLess(item['core_gauss_curvature_max'],0)
        self.assertLess(a['257']['core_fourth_order_operator_residual_max'],.0011)
        self.assertLess(a['257']['core_fourth_order_operator_residual_max'],a['129']['core_fourth_order_operator_residual_max']/3)
        self.assertLess(a['129']['core_height_difference_at_normalized_coordinates'],.0061)
        self.assertLess(a['257h2']['core_height_difference_at_normalized_coordinates'],.0063)
