"""Audit exact ingredients; no claim to solve the matching or translator PDE."""
import cmath
import json
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from generate_su_gluing import ALPHA, EPSILON, PHI, Q, grim, neck, point
from test_lagrangian_geometry import geometry3


class SuGluingTests(unittest.TestCase):
    def test_input_intersection_and_characteristic_angle(self):
        self.assertAlmostEqual(abs(grim(0)-Q),0,places=13)
        self.assertAlmostEqual(abs(grim(0,1)-Q),0,places=13)
        tangents=[]
        for branch in (0,1):
            tangent=(grim(1e-5,branch)-grim(-1e-5,branch))/2e-5
            self.assertAlmostEqual(abs(tangent),1,places=9)
            tangents.append(cmath.phase(tangent))
        self.assertAlmostEqual(tangents[1]-tangents[0],PHI,places=9)
        self.assertAlmostEqual(3*PHI,math.pi,places=13)

    def test_symmetric_neck_is_lagrangian_and_minimal_in_c3(self):
        def full(a,b,s):
            w=neck(s,1)
            omega=[math.cos(a)*math.cos(b),math.sin(a)*math.cos(b),math.sin(b)]
            z=[w*omega[0],w*omega[1],Q+cmath.exp(1j*ALPHA)*w*omega[2]]
            return [c for x in z for c in (x.real,x.imag)]
        for s in [-7,-.5,0,.5,7]:
            self.assertAlmostEqual((neck(s)**3).imag,EPSILON**3,places=13)
        for p in [(.4,.7,-2),(.8,-.3,0),(1.2,.4,2)]:
            _,H,_,omega=geometry3(full,p)
            self.assertLess(max(abs(c) for c in H),2e-6)
            self.assertLess(omega,2e-7)

    def test_outer_matching_is_exactly_on_each_grim_input(self):
        for eta in [-8,8]:
            for theta in [.3,1.4,3.1,5.7]:
                p,_=point(theta,eta)
                branch=int(eta<0);r=abs(neck(math.sinh(eta)))
                self.assertLess(abs(complex(p[2],p[3])-grim(r*math.sin(theta),branch)),1e-13)
                self.assertLess(abs(complex(p[0],p[1])-cmath.exp(1j*branch*PHI)*r*math.cos(theta)),1e-13)

    def test_slice_has_two_display_boundaries_and_no_unjoined_seam(self):
        from collections import Counter,defaultdict
        data=json.loads((ROOT/'site/assets/solitons/su-glued-translators.json').read_text())
        edges=Counter(tuple(sorted((a,b))) for f in data['faces'] for a,b in zip(f,f[1:]+f[:1]))
        self.assertTrue(all(n in (1,2) for n in edges.values()))
        adj=defaultdict(set)
        for (a,b),n in edges.items():
            if n==1:adj[a].add(b);adj[b].add(a)
        self.assertTrue(all(len(a)==2 for a in adj.values()))
        remaining=set(adj);components=0
        while remaining:
            stack=[remaining.pop()];components+=1
            while stack:
                for n in adj[stack.pop()]:
                    if n in remaining:remaining.remove(n);stack.append(n)
        self.assertEqual(components,2)
        self.assertEqual(len(data['vertices'])-len(edges)+len(data['faces']),0)
        self.assertEqual(data['status'],'schematic')


if __name__=='__main__':unittest.main()
