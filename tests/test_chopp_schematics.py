"""Check drawing topology without importing the scientific regeneration stack."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def components(graph):
    remaining, count = set(graph), 0
    while remaining:
        pending = [remaining.pop()]
        count += 1
        while pending:
            for other in graph[pending.pop()] & remaining:
                remaining.remove(other)
                pending.append(other)
    return count


class ChoppSchematicsTests(unittest.TestCase):
    def test_committed_meshes_have_the_reported_drawing_topology(self):
        cases = {'cube': (5, 0), 'octahedron': (7, 0), 'saddle': (1, 1),
                 'two-handle': (1, 2), 'four-handle': (3, 2)}
        for name, (genus, ends) in cases.items():
            with self.subTest(name=name):
                mesh = json.loads((ROOT / f'site/assets/solitons/chopp-{name}.json').read_text())
                vertices, faces = mesh['vertices'], mesh['faces']
                edges, directions = Counter(), Counter()
                neighbors, boundary = defaultdict(set), defaultdict(set)
                used = set()
                for face in faces:
                    self.assertEqual(len(set(face)), 3)
                    used.update(face)
                    for a, b in zip(face, face[1:]+face[:1]):
                        edges[tuple(sorted((a, b)))] += 1
                        directions[(a, b)] += 1
                self.assertEqual(used, set(range(len(vertices))))
                for (a, b), count in edges.items():
                    self.assertIn(count, (1, 2))
                    neighbors[a].add(b)
                    neighbors[b].add(a)
                    if count == 1:
                        boundary[a].add(b)
                        boundary[b].add(a)
                    else:
                        self.assertEqual(directions[(a, b)], 1)
                        self.assertEqual(directions[(b, a)], 1)
                self.assertEqual(components(neighbors), 1)
                self.assertTrue(all(len(adjacent) == 2 for adjacent in boundary.values()))
                self.assertEqual(components(boundary), ends)
                self.assertEqual(len(vertices)-len(edges)+len(faces), 2-2*genus-ends)
                self.assertEqual(mesh['status'], 'schematic')
                self.assertNotIn('dynamic', mesh)


if __name__ == '__main__':
    unittest.main()
