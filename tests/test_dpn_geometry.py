"""Audit committed illustration topology independently of the mesh generator."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1]/'site/assets/solitons'

def components(graph):
    remaining, count = set(graph), 0
    while remaining:
        pending = [remaining.pop()]; count += 1
        while pending:
            for b in graph[pending.pop()] & remaining:
                remaining.remove(b); pending.append(b)
    return count

class DpnGeometryTests(unittest.TestCase):
    def test_schematics_have_three_end_rims_and_expected_topology(self):
        for m in [8,12,16]:
            suffix='' if m==12 else f'-{m}'
            d=json.loads((ASSETS/f'bowl-catenoid-gluing{suffix}.json').read_text())
            v,f=d['vertices'],d['faces'];edges=Counter()
            graph,boundary=defaultdict(set),defaultdict(set)
            for tri in f:
                self.assertEqual(len(set(tri)),3)
                for a,b in zip(tri,tri[1:]+tri[:1]):
                    self.assertTrue(0<=a<len(v) and 0<=b<len(v))
                    edges[tuple(sorted((a,b)))]+=1;graph[a].add(b);graph[b].add(a)
            self.assertEqual(set(edges.values()),{1,2})
            for (a,b),n in edges.items():
                if n==1:boundary[a].add(b);boundary[b].add(a)
            self.assertEqual(components(graph),1)
            self.assertEqual(components(boundary),3)
            self.assertTrue(all(len(n)==2 for n in boundary.values()))
            self.assertTrue(all(abs(v[i][2]-4.4)<1e-5 for i in boundary))
            chi=len(v)-len(edges)+len(f)
            self.assertEqual(chi,1-2*m)
            self.assertEqual(d['modelGenus'],m-1)
            self.assertEqual(d['status'],'schematic')
            self.assertEqual(len(v),len(d['vertexColors']))
            self.assertTrue(all(math.isfinite(x) for p in v for x in p))

    def test_numerical_profiles_have_single_crossing_and_correct_ode(self):
        d=json.loads((ASSETS/'dpn-bowl-catenoid-input.json').read_text())
        bowl,upper,lower=d['meridians']
        self.assertEqual(bowl[0],[0.,0.])
        self.assertAlmostEqual(upper[0][0],1.)
        self.assertEqual(upper[0],lower[0])
        self.assertTrue(all(abs(p[-1][1]-4.4)<1e-10 for p in [bowl,upper,lower]))
        def interp(curve,r):
            for a,b in zip(curve,curve[1:]):
                if a[0]<=r<=b[0]:return a[1]+(r-a[0])/(b[0]-a[0])*(b[1]-a[1])
            raise ValueError(r)
        self.assertAlmostEqual(interp(bowl,1.4),interp(lower,1.4),delta=3e-4)
        self.assertGreater(interp(upper,1.4),interp(bowl,1.4)+1.)
        differences=[interp(lower,1+2*i/100)-interp(bowl,1+2*i/100) for i in range(101)]
        self.assertEqual(sum(a*b<0 for a,b in zip(differences,differences[1:])),1)
        # Independent finite-difference check on the graph equation away from waist.
        for curve in [bowl,upper,lower]:
            errors=[]
            for a,b,c in zip(curve[:-1],curve[1:-1],curve[2:-1]):
                r,z=b;left=r-a[0];right=c[0]-r
                if r<1.3 or min(left,right)<1e-6:continue
                pl=(z-a[1])/left;pr=(c[1]-z)/right
                p=(pl*right+pr*left)/(left+right)
                pp=2*(pr-pl)/(left+right)
                errors.append(abs(pp/(1+p*p)+p/r-1))
            self.assertLess(max(errors),.02)
        self.assertEqual(d['status'],'numerical-ode')

if __name__=='__main__':unittest.main()
