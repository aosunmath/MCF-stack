"""Topology of the drawing mesh; no claim to verify the shrinker PDE."""
from collections import Counter
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'site/assets/solitons'


def connected(graph):
    seen = set(); pending = [next(iter(graph))]
    while pending:
        v = pending.pop()
        if v not in seen:
            seen.add(v); pending.extend(graph[v]-seen)
    return len(seen) == len(graph)


class SphericalDoublingTests(unittest.TestCase):
    def test_closed_orientable_connected_mesh_and_genus(self):
        for m in [6, 10, 14]:
            with self.subTest(m=m):
                name = 'sphere-doubling-shrinker' + ('' if m == 10 else f'-{m}')
                data = json.loads((ASSETS/(name+'.json')).read_text())
                vertices, faces = data['vertices'], data['faces']
                self.assertEqual(data['status'], 'schematic')
                self.assertEqual(data['genus'], 2*m-1)
                edges = Counter(); directions = Counter()
                adjacency = {i:set() for i in range(len(vertices))}
                links = [{} for _ in vertices]
                for a, b, c in faces:
                    self.assertEqual(len({a,b,c}), 3)
                    for u,v,w in [(a,b,c),(b,c,a),(c,a,b)]:
                        edge=tuple(sorted((u,v))); edges[edge]+=1
                        directions[edge]+=1 if u<v else -1
                        adjacency[u].add(v); adjacency[v].add(u)
                        links[u].setdefault(v,set()).add(w)
                        links[u].setdefault(w,set()).add(v)
                self.assertEqual(set(edges.values()), {2})
                self.assertTrue(all(v==0 for v in directions.values()))
                self.assertTrue(connected(adjacency))
                for link in links:
                    self.assertTrue(all(len(v)==2 for v in link.values()))
                    self.assertTrue(connected(link))
                self.assertEqual(len(vertices)-len(edges)+len(faces), 4-4*m)
                self.assertEqual(len(data['vertexGroups']), len(vertices))
                self.assertEqual(len(data['normals']), len(vertices))
                self.assertTrue(all(abs(math.hypot(*n)-1)<2e-6 for n in data['normals']))
                self.assertEqual(len(data['faceGroups']), len(faces))
                self.assertEqual(len(data['sites']), 2*m)
                for lower,upper in zip(data['sites'][:m], data['sites'][m:]):
                    self.assertAlmostEqual(math.hypot(*lower), 2, places=8)
                    self.assertEqual(lower[:2], upper[:2])
                    self.assertEqual(lower[2], -upper[2])
                # Each complete neck has a waist circle on the radius-two sphere.
                waists=[p for p in vertices if abs(math.hypot(*p)-2)<1e-7]
                self.assertEqual(len(waists), 2*m*data['construction']['segments'])
                self.assertTrue(all(1.7<math.hypot(*p)<2.3 for p in vertices))

    def test_linearized_guide_is_explicitly_separate_from_solved_geometry(self):
        audit=json.loads((ASSETS/'sphere-doubling-audit.json').read_text())
        self.assertEqual(audit['status'],'schematic')
        self.assertLess(audit['flux_balance_residual'],1e-10)
        self.assertLess(audit['refined_latitude_s_change'],1e-10)
        self.assertTrue(33.5<audit['latitude_degrees']<33.6)
        self.assertEqual(set(audit['models']),{'6','10','14'})


if __name__ == '__main__':
    unittest.main()
