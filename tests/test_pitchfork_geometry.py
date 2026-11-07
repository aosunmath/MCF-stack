"""Geometric checks on the explicitly labeled drawing, not a PDE certificate."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[1]/'site/assets/solitons/pitchfork-surface.json'


def connected(graph):
    visited=set();todo=[next(iter(graph))]
    while todo:
        v=todo.pop()
        if v not in visited:
            visited.add(v);todo.extend(graph[v]-visited)
    return visited==set(graph)


class PitchforkGeometryTests(unittest.TestCase):
    def test_clipped_mesh_is_one_manifold_disk_with_a_shared_axis(self):
        d=json.loads(DATA.read_text());v,f=d['vertices'],d['faces']
        self.assertEqual(d['status'],'schematic');self.assertAlmostEqual(d['halfWidth'],math.pi)
        self.assertLess(len(v),65536)
        edges=Counter(tuple(sorted((face[k],face[(k+1)%3]))) for face in f for k in range(3))
        graph=defaultdict(set);boundary=defaultdict(set)
        directed=Counter((face[k],face[(k+1)%3]) for face in f for k in range(3))
        for (a,b),count in edges.items():
            self.assertIn(count,[1,2]);graph[a].add(b);graph[b].add(a)
            if count==1:boundary[a].add(b);boundary[b].add(a)
            else:self.assertEqual(directed[a,b],directed[b,a])
        self.assertTrue(connected(graph));self.assertTrue(connected(boundary))
        self.assertTrue(all(len(neighbors)==2 for neighbors in boundary.values()))
        self.assertEqual(len(v)-len(edges)+len(f),1)
        axis=d['paths'][0]
        self.assertEqual(len(axis),145)
        self.assertTrue(all(v[i][0]==0 and v[i][1]==0 for i in axis))
        self.assertTrue(all(edges[tuple(sorted((a,b)))]==2 for a,b in zip(axis,axis[1:])))
        points={tuple(round(c,6) for c in p) for p in v}
        for x,y,z in v:self.assertTrue((round(-x,6),round(-y,6),round(z,6)) in points, 'Missing half-turn partner')

    def test_drawing_normals_are_finite_and_its_curvature_is_negative(self):
        d=json.loads(DATA.read_text())
        self.assertEqual(len(d['normals']),len(d['vertices']))
        for (_,y,z),n in zip(d['vertices'],d['normals']):
            self.assertTrue(all(math.isfinite(c) for c in n))
            self.assertAlmostEqual(sum(c*c for c in n),1,places=6)
            fyy=-.5*math.sin(y)*math.exp(z)-.5/math.cos(y/2)**2*math.tan(y/2)
            fzz=.5*math.sin(y)*math.exp(z);fyz=.5*math.cos(y)*math.exp(z)+1
            self.assertLess(fyy*fzz-fyz*fyz,0)


if __name__=='__main__':unittest.main()
