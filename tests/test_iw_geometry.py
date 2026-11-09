"""Independent topology checks on the drawing, not on a solved shrinker."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest
from test_bns_geometry import components

ASSETS = Path(__file__).resolve().parents[1] / 'site/assets/solitons'


class IlmanenWhiteGeometryTests(unittest.TestCase):
    def test_connected_orientable_two_ended_models_and_neck_counts(self):
        for genus in [2, 3, 5, 11]:
            with self.subTest(genus=genus):
                suffix = '' if genus == 3 else f'-{genus}'
                d = json.loads((ASSETS/f'iw-two-ended{suffix}.json').read_text())
                self.assertEqual(d['status'], 'schematic')
                self.assertEqual(d['genus'], genus)
                self.assertEqual(d['kind'], 'iw-schematic')
                v, f = d['vertices'], d['faces']
                self.assertLess(len(v), 65536)
                edges, directions = Counter(), Counter()
                graph, boundary, waist = defaultdict(set), defaultdict(set), defaultdict(set)
                links = [defaultdict(set) for _ in v]
                for face in f:
                    self.assertEqual(len(set(face)), 3)
                    crossings = []
                    for a, b, c in [face, face[1:]+face[:1], face[2:]+face[:2]]:
                        key = tuple(sorted((a, b)))
                        edges[key] += 1
                        directions[key] += 1 if a < b else -1
                        links[a][b].add(c); links[a][c].add(b)
                        if (v[a][2] < 0) != (v[b][2] < 0):
                            crossings.append(key)
                    if crossings:
                        self.assertEqual(len(crossings), 2)
                        a, b = crossings; waist[a].add(b); waist[b].add(a)
                for (a, b), count in edges.items():
                    graph[a].add(b); graph[b].add(a)
                    if count == 1:
                        boundary[a].add(b); boundary[b].add(a)
                    else:
                        self.assertEqual(directions[(a, b)], 0)
                self.assertEqual(set(edges.values()), {1, 2})
                self.assertEqual(components(graph), 1)
                self.assertEqual(components(boundary), 2)
                self.assertTrue(all(len(n) == 2 for n in boundary.values()))
                self.assertEqual(len(v)-len(edges)+len(f), -2*genus)
                self.assertEqual(components(waist), genus+1)
                self.assertTrue(all(len(n) == 2 for n in waist.values()))
                overlay = defaultdict(set)
                for a, b in d['equator']:
                    self.assertEqual(a[2], 0); self.assertEqual(b[2], 0)
                    overlay[tuple(a)].add(tuple(b)); overlay[tuple(b)].add(tuple(a))
                self.assertEqual(components(overlay), genus+1)
                self.assertTrue(all(len(n) == 2 for n in overlay.values()))
                for j, link in enumerate(links):
                    self.assertEqual(components(link), 1)
                    degrees = Counter(len(n) for n in link.values())
                    self.assertEqual(degrees[1], 2 if j in boundary else 0)
                    self.assertTrue(set(degrees) <= {1, 2})
                for j in boundary:
                    self.assertAlmostEqual(math.hypot(*v[j][:2]), 4.6, places=5)
                self.assertEqual(len(d['normals']), len(v))
                for point, normal in zip(v, d['normals']):
                    self.assertTrue(all(math.isfinite(x) for x in point+normal))
                    self.assertAlmostEqual(math.hypot(*normal), 1, places=5)


if __name__ == '__main__': unittest.main()
