"""Topology of the schematic only; this does not test the shrinker equation."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'site/assets/solitons'


def components(graph):
    unseen = set(graph); count = 0
    while unseen:
        count += 1; queue = [unseen.pop()]
        while queue:
            for v in graph[queue.pop()]:
                if v in unseen:
                    unseen.remove(v); queue.append(v)
    return count


class ShaoZouGeometryTests(unittest.TestCase):
    def test_connected_orientable_surface_with_expected_genus_and_ends(self):
        for k in [2, 3, 4, 5, 6]:
            for m in [6, 10, 14]:
                with self.subTest(k=k, m=m):
                    suffix = '' if (k,m)==(4,10) else f'-{k}-{m}'
                    data = json.loads((ASSETS/f'shao-zou-stacking{suffix}.json').read_text())
                    vertices, faces = data['vertices'], data['faces']
                    self.assertEqual(data['status'], 'schematic')
                    self.assertLess(len(vertices), 65536)
                    self.assertEqual(len(data['vertexGroups']), len(vertices))
                    edges = Counter(); directions = Counter(); adjacency = defaultdict(set)
                    links = [defaultdict(set) for _ in vertices]
                    for a,b,c in faces:
                        self.assertEqual(len({a,b,c}), 3)
                        for u,v,w in [(a,b,c),(b,c,a),(c,a,b)]:
                            edge = tuple(sorted((u,v))); edges[edge] += 1
                            directions[edge] += 1 if u<v else -1
                            adjacency[u].add(v); adjacency[v].add(u)
                            links[u][v].add(w); links[u][w].add(v)
                    self.assertEqual(set(edges.values()), {1,2})
                    self.assertTrue(all(directions[e]==0 for e,n in edges.items() if n==2))
                    self.assertEqual(components(adjacency), 1)
                    self.assertEqual(len(adjacency), len(vertices))
                    boundary = defaultdict(set)
                    for (a,b), n in edges.items():
                        if n==1:
                            boundary[a].add(b); boundary[b].add(a)
                    self.assertTrue(all(len(v)==2 for v in boundary.values()))
                    self.assertEqual(components(boundary), k)
                    for i in boundary:
                        self.assertAlmostEqual(math.hypot(*vertices[i][:2]), 3.2, places=5)
                    for i,link in enumerate(links):
                        self.assertEqual(components(link), 1)
                        degrees = Counter(map(len,link.values()))
                        self.assertEqual(degrees[1], 2 if i in boundary else 0)
                        self.assertTrue(set(degrees)<={1,2})
                    chi = len(vertices)-len(edges)+len(faces)
                    self.assertEqual(2-k-chi, 2*(k-1)*(m-1))
                    sites = data['construction']['sites']
                    self.assertEqual(len(sites), k-1)
                    for g,ring in enumerate(sites):
                        self.assertEqual(len(ring), m)
                        self.assertAlmostEqual(math.atan2(ring[0][1],ring[0][0]), (g%2)*math.pi/m)
                    patch = data['construction']['patch_radius']
                    radius = data['construction']['balanced_radius']
                    self.assertLess(2*patch, 2*radius*math.sin(math.pi/(2*m)))

    def test_radius_guide_remains_separate_from_nonlinear_geometry(self):
        audit = json.loads((ASSETS/'shao-zou-audit.json').read_text())
        self.assertEqual(audit['status'], 'schematic')
        self.assertAlmostEqual(audit['balanced_radius'], 1.51860011206547, places=10)
        self.assertLess(audit['radius_balance_residual'], 1e-12)
        self.assertEqual(len(audit['models']), 15)


if __name__ == '__main__': unittest.main()
