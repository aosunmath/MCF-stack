"""Audit the topology of the illustration, not existence of HMW expanders."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'site/assets/solitons'


def components(graph):
    unseen = set(graph); result = []
    while unseen:
        group = {unseen.pop()}; pending = list(group)
        while pending:
            for b in graph[pending.pop()] & unseen:
                unseen.remove(b); group.add(b); pending.append(b)
        result.append(group)
    return result


class ExpanderTopologyTests(unittest.TestCase):
    def test_meshes_have_three_ends_and_the_advertised_genus(self):
        for m in [4, 12, 20]:
            with self.subTest(m=m):
                suffix = '' if m == 4 else f'-{m}'
                data = json.loads((ASSETS/f'high-genus-expanders{suffix}.json').read_text())
                vertices, faces = data['vertices'], data['faces']
                edges = Counter(); directed = Counter(); graph = defaultdict(set); boundary = defaultdict(set)
                for face in faces:
                    self.assertEqual(len(set(face)), 3)
                    for a, b in zip(face, face[1:]+face[:1]):
                        self.assertTrue(0 <= a < len(vertices))
                        edges[tuple(sorted([a, b]))] += 1; directed[a, b] += 1
                        graph[a].add(b); graph[b].add(a)
                self.assertEqual(set(edges.values()), {1, 2})
                for (a, b), n in edges.items():
                    if n == 1:
                        boundary[a].add(b); boundary[b].add(a)
                    else:
                        self.assertEqual(directed[a, b], 1)
                        self.assertEqual(directed[b, a], 1)
                self.assertEqual(len(components(graph)), 1)
                self.assertTrue(all(len(v) == 2 for v in boundary.values()))
                self.assertEqual(len(components(boundary)), 3)
                self.assertEqual(len(vertices)-len(edges)+len(faces), 1-2*m)
                self.assertEqual(data['genus'], m-1)
                self.assertEqual(data['status'], 'schematic')
                # All three mesh ends approximate one common explicitly chosen cone.
                slope = data['cone']['slope']
                for i in boundary:
                    x, y, z = vertices[i]; r = math.hypot(x, y)
                    self.assertAlmostEqual(r, 3.5, places=5)
                    target = .035*r*math.cos(4*math.atan2(y, x))
                    self.assertAlmostEqual(data['endShear'][i], target, places=5)
                    self.assertLess(min(abs(z/r-j*slope) for j in [-1, 0, 1]), .002)


if __name__ == '__main__':
    unittest.main()
