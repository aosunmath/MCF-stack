"""Check the exported illustration's topology independently of its generator."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'site/assets/solitons'


def components(graph):
    unseen = set(graph)
    count = 0
    while unseen:
        todo = [unseen.pop()]
        count += 1
        while todo:
            for v in graph[todo.pop()] & unseen:
                unseen.remove(v)
                todo.append(v)
    return count


class BnsGeometryTests(unittest.TestCase):
    def test_models_have_the_advertised_genus_and_one_truncation_boundary(self):
        for genus in [1, 2, 3, 5, 11]:
            with self.subTest(genus=genus):
                suffix = '' if genus == 3 else f'-{genus}'
                d = json.loads((ASSETS/f'bns-shrinkers{suffix}.json').read_text())
                self.assertEqual(d['status'], 'schematic')
                self.assertEqual(d['genus'], genus)
                v, f = d['vertices'], d['faces']
                self.assertEqual(len(d['normals']), len(v))
                self.assertLess(len(v), 65536)
                edges = Counter()
                graph, boundary = defaultdict(set), defaultdict(set)
                for face in f:
                    self.assertEqual(len(set(face)), 3)
                    self.assertTrue(all(0 <= j < len(v) for j in face))
                    for a, b in zip(face, face[1:]+face[:1]):
                        edges[tuple(sorted((a, b)))] += 1
                for (a, b), count in edges.items():
                    graph[a].add(b); graph[b].add(a)
                    if count == 1:
                        boundary[a].add(b); boundary[b].add(a)
                self.assertEqual(set(edges.values()), {1, 2})
                self.assertEqual(components(graph), 1)
                self.assertEqual(components(boundary), 1)
                self.assertTrue(all(len(n) == 2 for n in boundary.values()))
                self.assertEqual(len(v)-len(edges)+len(f), 1-2*genus)
                for j in boundary:
                    self.assertAlmostEqual(math.hypot(*v[j][:2]), 5, places=5)
                for point, normal in zip(v, d['normals']):
                    self.assertTrue(all(math.isfinite(x) for x in point+normal))
                    self.assertAlmostEqual(math.hypot(*normal), 1, places=5)


if __name__ == '__main__':
    unittest.main()
