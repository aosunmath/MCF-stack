"""Audit the drawing's topology and face-center arrangements, not the PDE."""
from collections import Counter
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'site/assets/solitons'
CASES = [('tetrahedron', 4), ('cube', 6), ('octahedron', 8),
         ('dodecahedron', 12), ('icosahedron', 20)]


def connected(graph):
    seen = set(); pending = [next(iter(graph))]
    while pending:
        v = pending.pop()
        if v not in seen:
            seen.add(v); pending.extend(graph[v]-seen)
    return len(seen) == len(graph)


class PlatonicGeometryTests(unittest.TestCase):
    def test_closed_orientable_surface_with_expected_genus_and_necks(self):
        for solid, count in CASES:
            with self.subTest(solid=solid):
                suffix = '' if solid == 'cube' else '-'+solid
                data = json.loads((ASSETS/('ketover-platonic'+suffix+'.json')).read_text())
                vertices, faces = data['vertices'], data['faces']
                self.assertEqual(data['status'], 'schematic')
                self.assertEqual(data['necks'], count)
                self.assertEqual(data['genus'], count-1)
                edges, directions = Counter(), Counter()
                adjacency = {i: set() for i in range(len(vertices))}
                links = [{} for _ in vertices]
                for a, b, c in faces:
                    self.assertEqual(len({a, b, c}), 3)
                    for u, v, w in [(a, b, c), (b, c, a), (c, a, b)]:
                        edge = tuple(sorted((u, v))); edges[edge] += 1
                        directions[edge] += 1 if u < v else -1
                        adjacency[u].add(v); adjacency[v].add(u)
                        links[u].setdefault(v, set()).add(w)
                        links[u].setdefault(w, set()).add(v)
                self.assertEqual(set(edges.values()), {2})
                self.assertEqual(set(directions.values()), {0})
                self.assertTrue(connected(adjacency))
                for link in links:
                    self.assertTrue(all(len(v) == 2 for v in link.values()))
                    self.assertTrue(connected(link))
                self.assertEqual(len(vertices)-len(edges)+len(faces), 4-2*count)
                self.assertEqual(len(data['normals']), len(vertices))
                self.assertEqual(len(data['vertexGroups']), len(vertices))
                self.assertEqual(len(data['faceGroups']), len(faces))
                self.assertTrue(all(abs(math.hypot(*n)-1) < 2e-6 for n in data['normals']))
                self.assertTrue(all(all(math.isfinite(x) for x in p) for p in vertices))
                # Each radial throat closes around its own face-center direction.
                waists = {i for i, p in enumerate(vertices) if abs(math.hypot(*p)-2) < 1e-7}
                self.assertEqual(len(waists), count*data['construction']['segments'])
                waist_graph = {i: adjacency[i] & waists for i in waists}
                self.assertTrue(all(len(v) == 2 for v in waist_graph.values()))
                remaining = set(waists); components = 0
                while remaining:
                    pending = [next(iter(remaining))]; component = set()
                    while pending:
                        i = pending.pop()
                        if i not in component:
                            component.add(i); pending.extend(waist_graph[i]-component)
                    self.assertEqual(len(component), data['construction']['segments'])
                    remaining -= component; components += 1
                self.assertEqual(components, count)
                sites = data['sites']
                self.assertEqual(len(sites), count)
                self.assertTrue(all(abs(math.hypot(*p)-2) < 1e-8 for p in sites))
                # A regular polyhedron has identical angular data at every face.
                spectra = [sorted(round(sum(a*b for a, b in zip(p, q))/4, 7)
                                  for q in sites) for p in sites]
                self.assertTrue(all(s == spectra[0] for s in spectra))
                if solid == 'cube':
                    self.assertTrue(all(sum(abs(x) > 1e-8 for x in p) == 1 for p in sites))
                if solid == 'octahedron':
                    self.assertTrue(all(abs(abs(x)-2/math.sqrt(3)) < 1e-8 for p in sites for x in p))
                gap = data['construction']['half_gap']
                self.assertGreater(2-1.8*gap, 0)
                audit = json.loads((ASSETS/'platonic-audit.json').read_text())['models'][solid]
                self.assertLess(data['construction']['patch_radius'], audit['minimum_site_angle'])


if __name__ == '__main__':
    unittest.main()
