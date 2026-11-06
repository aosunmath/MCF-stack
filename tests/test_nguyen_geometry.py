"""Audit the drawing's topology and the separately meshed exact ingredient."""
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
import unittest

ASSETS=Path(__file__).resolve().parents[1]/'site/assets/solitons'


def reachable(graph):
    visited=set(); pending=[next(iter(graph))]
    while pending:
        a=pending.pop()
        if a not in visited:
            visited.add(a); pending.extend(graph[a]-visited)
    return visited


class NguyenGeometryTests(unittest.TestCase):
    def test_connected_orientable_meshes_have_genus_m_minus_one_and_one_end_cut(self):
        for m in [6,10,14]:
            with self.subTest(m=m):
                name='nguyen-m-saddles' if m==10 else f'nguyen-m-saddles-{m}'
                d=json.loads((ASSETS/(name+'.json')).read_text()); v,f=d['vertices'],d['faces']
                self.assertEqual(d['status'],'schematic')
                self.assertEqual(d['genus'],m-1)
                self.assertEqual(len(v),len(d['vertexColors']))
                self.assertLess(len(v),65536)
                edges=Counter(tuple(sorted((face[i],face[(i+1)%3]))) for face in f for i in range(3))
                oriented=Counter((face[i],face[(i+1)%3]) for face in f for i in range(3))
                graph=defaultdict(set); boundary=defaultdict(set)
                for (a,b),n in edges.items():
                    self.assertIn(n,[1,2]); graph[a].add(b);graph[b].add(a)
                    if n==2:self.assertEqual(oriented[a,b],oriented[b,a])
                    else:boundary[a].add(b);boundary[b].add(a)
                self.assertEqual(len(reachable(graph)),len(v))
                self.assertEqual(reachable(boundary),set(boundary))
                self.assertTrue(all(len(n)==2 for n in boundary.values()))
                self.assertEqual(len(v)-len(edges)+len(f),1-2*(m-1))
                for i in boundary:self.assertAlmostEqual(math.hypot(*v[i][:2]),3.65,places=5)
                links=defaultdict(lambda:defaultdict(set))
                for face in f:
                    self.assertEqual(len(set(face)),3)
                    for i,a in enumerate(face):
                        b,c=face[(i+1)%3],face[(i+2)%3]
                        links[a][b].add(c);links[a][c].add(b)
                for a,link in links.items():
                    self.assertEqual(reachable(link),set(link))
                    self.assertEqual(sorted(len(n) for n in link.values()).count(1),2 if a in boundary else 0)

    def test_unwrapped_ingredient_vertices_satisfy_the_source_equation(self):
        d=json.loads((ASSETS/'nguyen-scherk-detail.json').read_text())
        self.assertEqual(d['status'],'exact-ingredient-mesh')
        self.assertEqual(len(d['vertices']),len(d['vertexColors']))
        for y,x,z in d['vertices']:
            self.assertLess(abs(math.sin(y)-math.sinh(x)*math.sinh(z)),3e-7)
        self.assertGreater(max(p[0] for p in d['vertices']),6.28)
        self.assertLess(min(p[0] for p in d['vertices']),-6.28)


if __name__=='__main__':unittest.main()
