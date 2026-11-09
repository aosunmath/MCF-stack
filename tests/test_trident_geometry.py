"""Validate the connected drawing and its display cuts, not the translator PDE."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest
from test_nguyen_geometry import reachable

ASSETS=Path(__file__).resolve().parents[1]/'site/assets/solitons'


class TridentGeometryTests(unittest.TestCase):
    def test_connected_orientable_three_period_crops(self):
        for scale in [22,35,50]:
            with self.subTest(scale=scale):
                suffix='' if scale==35 else f'-{scale}'
                d=json.loads((ASSETS/f'nguyen-tridents{suffix}.json').read_text())
                v,f=d['vertices'],d['faces'];eps=d['epsilon']
                self.assertEqual(d['status'],'schematic')
                self.assertAlmostEqual(d['period'],2*math.pi*eps)
                self.assertEqual(len(v),len(d['vertexColors']))
                self.assertLess(len(v),65536)
                edges=Counter(tuple(sorted((face[i],face[(i+1)%3]))) for face in f for i in range(3))
                oriented=Counter((face[i],face[(i+1)%3]) for face in f for i in range(3))
                graph=defaultdict(set);boundary=defaultdict(set)
                for (a,b),n in edges.items():
                    self.assertIn(n,[1,2]);graph[a].add(b);graph[b].add(a)
                    if n==2:self.assertEqual(oriented[a,b],oriented[b,a])
                    else:boundary[a].add(b);boundary[b].add(a)
                self.assertEqual(len(reachable(graph)),len(v))
                first=reachable(boundary)
                remainder={k:val for k,val in boundary.items() if k not in first}
                self.assertTrue(remainder)
                self.assertEqual(reachable(remainder),set(remainder))
                self.assertTrue(all(len(n)==2 for n in boundary.values()))
                self.assertEqual(len(v)-len(edges)+len(f),-4)
                lo,hi=d['construction']['bounds']
                for i in boundary:
                    self.assertLess(min(abs(v[i][j]-b[j]) for j in range(3) for b in [lo,hi]),2e-5)
                links=defaultdict(lambda:defaultdict(set))
                for face in f:
                    self.assertEqual(len(set(face)),3)
                    for i,a in enumerate(face):
                        b,c=face[(i+1)%3],face[(i+2)%3]
                        links[a][b].add(c);links[a][c].add(b)
                for a,link in links.items():
                    self.assertEqual(reachable(link),set(link))
                    self.assertEqual(sorted(len(n) for n in link.values()).count(1),2 if a in boundary else 0)
                for x,y,z in v:
                    u=(z+math.log(math.cos(y)))/eps
                    w=math.asinh(math.tan(y))/eps
                    residual=math.tanh(u)*math.tanh(w)-math.sin(x/eps)/math.cosh(u)/math.cosh(w)
                    self.assertLess(abs(residual),2e-6)

if __name__=='__main__':unittest.main()
