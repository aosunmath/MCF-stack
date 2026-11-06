"""Topology of the displayed construction meshes, not a shrinker existence test."""
import json
from pathlib import Path
from collections import Counter, defaultdict
import unittest

ASSETS=Path(__file__).resolve().parents[1]/'site/assets/solitons'


class KKMGeometryTests(unittest.TestCase):
    def test_each_schematic_is_connected_with_the_stated_genus_and_one_boundary(self):
        for k in (6,9,12):
            with self.subTest(periods=k):
                name='kkm-shrinker' if k==9 else f'kkm-shrinker-{k}'
                data=json.loads((ASSETS/(name+'.json')).read_text())
                v,f=data['vertices'],data['faces']
                self.assertEqual(data['status'],'schematic')
                self.assertEqual(data['construction']['periods'],k)
                self.assertEqual(data['construction']['genus'],k-1)
                self.assertEqual(len(v),len(data['construction']['endWeights']))
                self.assertEqual(len(f),len(data['faceColors']))
                edges=Counter(tuple(sorted((face[j],face[(j+1)%3]))) for face in f for j in range(3))
                self.assertEqual(set(edges.values()),{1,2})
                graph=defaultdict(set);boundary=defaultdict(set)
                for (a,b),n in edges.items():
                    graph[a].add(b);graph[b].add(a)
                    if n==1:boundary[a].add(b);boundary[b].add(a)
                def reachable(graph):
                    visited=set();pending=[next(iter(graph))]
                    while pending:
                        a=pending.pop()
                        if a in visited:continue
                        visited.add(a);pending.extend(graph[a]-visited)
                    return visited
                self.assertEqual(len(reachable(graph)),len(v))
                self.assertEqual(reachable(boundary),set(boundary))
                self.assertTrue(all(len(neighbors)==2 for neighbors in boundary.values()))
                self.assertEqual(len(v)-len(edges)+len(f),1-2*(k-1))
                for i in boundary:
                    self.assertAlmostEqual((v[i][0]**2+v[i][1]**2)**.5,3.65,places=5)
                # Each vertex link is connected: excludes pinched vertices that
                # an Euler count and edge-incidence check alone would miss.
                links=defaultdict(lambda:defaultdict(set))
                for face in f:
                    self.assertEqual(len(set(face)),3)
                    for j,a in enumerate(face):
                        b,c=face[(j+1)%3],face[(j+2)%3]
                        links[a][b].add(c);links[a][c].add(b)
                for a,link in links.items():
                    self.assertEqual(reachable(link),set(link))
                    self.assertEqual(sorted(len(n) for n in link.values()).count(1),2 if a in boundary else 0)


if __name__=='__main__':unittest.main()
