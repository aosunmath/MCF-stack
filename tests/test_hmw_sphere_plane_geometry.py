"""Check the illustrated topology, not the unsolved shrinker equation."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1]/'site/assets/solitons'


def connected(graph):
    reached = set(); pending = [next(iter(graph))]
    while pending:
        a = pending.pop()
        if a not in reached:
            reached.add(a); pending.extend(graph[a]-reached)
    return reached == set(graph)


class HmwGeometryTests(unittest.TestCase):
    def test_surface_is_connected_orientable_manifold_with_claimed_genus(self):
        for g in [3, 5, 11]:
            with self.subTest(g=g):
                name = 'hmw-one-ended' if g == 5 else f'hmw-one-ended-{g}'
                data = json.loads((ASSETS/(name+'.json')).read_text())
                v, f = data['vertices'], data['faces']
                self.assertEqual(data['status'], 'schematic')
                self.assertEqual(data['genus'], g)
                self.assertLess(len(v), 65536)
                self.assertEqual(len(v), len(data['normals']))
                edges = Counter(); orientation = Counter()
                graph = defaultdict(set); boundary = defaultdict(set)
                links = defaultdict(lambda: defaultdict(set))
                for face in f:
                    self.assertEqual(len(set(face)), 3)
                    for i, a in enumerate(face):
                        b, c = face[(i+1) % 3], face[(i+2) % 3]
                        self.assertTrue(0 <= a < len(v))
                        edge = tuple(sorted((a, b)))
                        edges[edge] += 1; orientation[edge] += 1 if a < b else -1
                        graph[a].add(b); graph[b].add(a)
                        links[a][b].add(c); links[a][c].add(b)
                for (a, b), count in edges.items():
                    self.assertIn(count, [1, 2])
                    if count == 2: self.assertEqual(orientation[a, b], 0)
                    else: boundary[a].add(b); boundary[b].add(a)
                self.assertTrue(connected(graph) and connected(boundary))
                self.assertTrue(all(len(n) == 2 for n in boundary.values()))
                self.assertEqual(len(v)-len(edges)+len(f), 1-2*g)
                for a, link in links.items():
                    self.assertTrue(connected(link))
                    degrees = [len(n) for n in link.values()]
                    self.assertTrue(all(n in [1, 2] for n in degrees))
                    self.assertEqual(degrees.count(1), 2 if a in boundary else 0)
                for a in boundary: self.assertAlmostEqual(math.hypot(*v[a][:2]), 3.8, places=5)

    def test_limit_vertices_lie_on_radius_two_sphere_or_plane(self):
        data = json.loads((ASSETS/'hmw-sphere-plane-limit.json').read_text())
        self.assertEqual(data['status'], 'exact-configuration-mesh')
        for x, y, z in data['vertices']:
            self.assertLess(min(abs(z), abs(math.sqrt(x*x+y*y+z*z)-2)), 1e-6)
        self.assertEqual(max(v[2] for v in data['vertices']), 2)
        self.assertEqual(min(v[2] for v in data['vertices']), -2)


if __name__ == '__main__': unittest.main()
