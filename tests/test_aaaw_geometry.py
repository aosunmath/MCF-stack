"""Independent checks of sampled profiles, not existence or end proofs."""
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'site/assets/solitons'


class AAAWGeometryTests(unittest.TestCase):
    def test_profiles_satisfy_arclength_equation_and_monotone_quantity(self):
        for name in ('rotator', 'yin-yang', 'screw', 'expanding', 'shrinking', 'spherical'):
            with self.subTest(name=name):
                data = json.loads((ASSETS/f'aaaw-{name}.json').read_text())
                d = data['integration']
                states, arc = d['states'], d['arc']
                alpha, omega, velocity = d['alpha'], d['omega'], d['velocity']
                previous_v = None
                for i, y in enumerate(states):
                    c, t = y[:3], y[3:]
                    self.assertAlmostEqual(sum(x*x for x in t), 1, places=9)
                    v = math.exp(alpha*sum(x*x for x in c)/2+velocity*c[2])*omega*(-c[1]*t[0]+c[0]*t[1])
                    if previous_v is not None:
                        self.assertGreaterEqual(v-previous_v, -1e-7*max(1, abs(v)))
                    previous_v = v
                    if i < 2 or i >= len(states)-2:
                        continue
                    h = (arc[i+1]-arc[i-1])/2
                    derivative = [(states[i-2][j]-8*states[i-1][j]+8*states[i+1][j]-states[i+2][j])/(12*h) for j in range(6)]
                    a = [alpha*c[0]-omega*c[1], alpha*c[1]+omega*c[0], alpha*c[2]+velocity]
                    dot = sum(x*z for x,z in zip(a,t))
                    expected = t + [a[j]-dot*t[j] for j in range(3)]
                    self.assertLess(max(abs(x-z) for x,z in zip(derivative,expected)), 5e-6)
                self.assertEqual(len(data['vertices']), len(states))
                self.assertEqual(data['paths'], [list(range(len(states)))])

    def test_spherical_profile_stays_on_the_correct_radius(self):
        data = json.loads((ASSETS/'aaaw-spherical.json').read_text())
        for x,y,z in data['vertices']:
            self.assertAlmostEqual(x*x+y*y+z*z, 2, places=6)
        states = data['integration']['states']
        self.assertAlmostEqual(states[len(states)//2][0], math.sqrt(2), places=10)

    def test_dense_curve_uses_irrational_frequency_without_false_closure(self):
        data = json.loads((ASSETS/'aaaw-dense-torus.json').read_text())
        vertices = data['vertices']
        for x,y,z,w in vertices:
            self.assertAlmostEqual(x*x+y*y, 1, places=6)
            self.assertAlmostEqual(z*z+w*w, 1, places=6)
        self.assertGreater(math.dist(vertices[0], vertices[-1]), .1)
        self.assertNotEqual(data['paths'][0][0], data['paths'][0][-1])


if __name__ == '__main__':
    unittest.main()
