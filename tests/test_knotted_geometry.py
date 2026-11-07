"""Topology and geometry of the drawing, not a self-expander PDE test."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'site/assets/solitons/knotted-expanders.json').read_text())


def components(graph):
    remaining=set(graph); groups=[]
    while remaining:
        group={remaining.pop()}; pending=list(group)
        while pending:
            for j in graph[pending.pop()] & remaining:
                remaining.remove(j); group.add(j); pending.append(j)
        groups.append(group)
    return groups


class KnottedGeometryTests(unittest.TestCase):
    def check_surface(self, model, count):
        v,f=model['vertices'],model['faces']
        self.assertLess(len(v),65536)
        self.assertEqual(len(model['vertexColors']),len(v))
        edges=Counter(tuple(sorted((face[i],face[(i+1)%3]))) for face in f for i in range(3))
        directed=Counter((face[i],face[(i+1)%3]) for face in f for i in range(3))
        graph=defaultdict(set); boundary=defaultdict(set); links=defaultdict(lambda:defaultdict(set))
        for face in f:
            self.assertEqual(len(set(face)),3)
            a,b,c=[v[i] for i in face];u=[b[i]-a[i] for i in range(3)];w=[c[i]-a[i] for i in range(3)]
            area2=math.hypot(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])
            self.assertGreater(area2,1e-10)
            for i,a in enumerate(face):
                b,c=face[(i+1)%3],face[(i+2)%3];links[a][b].add(c);links[a][c].add(b)
        for (a,b),n in edges.items():
            self.assertIn(n,[1,2]);graph[a].add(b);graph[b].add(a)
            if n==1:boundary[a].add(b);boundary[b].add(a)
            else:self.assertEqual(directed[a,b],directed[b,a])
        self.assertEqual(len(components(graph)),1)
        self.assertEqual(len(graph),len(v))
        self.assertEqual(len(components(boundary)),count)
        self.assertTrue(all(len(x)==2 for x in boundary.values()))
        self.assertEqual(len(v)-len(edges)+len(f),-count)  # genus 1
        for a,link in links.items():
            self.assertEqual(len(components(link)),1)
            degrees=[len(x) for x in link.values()]
            self.assertTrue(all(n in [1,2] for n in degrees))
            self.assertEqual(degrees.count(1),2 if a in boundary else 0)
        return components(boundary)

    def test_full_surface_has_exactly_three_rims_and_genus_one(self):
        self.assertEqual(DATA['status'],'schematic')
        rims=self.check_surface(DATA,3)
        used=set()
        for rim in rims:
            candidates=[j for j,n in enumerate(DATA['endAxes']) if max(abs(sum(DATA['vertices'][i][k]*n[k] for k in range(3))-5.2) for i in rim)<1e-6]
            self.assertEqual(len(candidates),1);used.update(candidates)
        self.assertEqual(used,{0,1,2})

    def test_closed_tube_is_a_closed_genus_one_auxiliary_surface(self):
        self.check_surface(DATA['core'],0)

    def test_spine_has_three_crossings_with_alternating_overpasses(self):
        p=DATA['spine'];events=[];count=0
        for i,a in enumerate(p):
            b=p[(i+1)%len(p)];u=[b[k]-a[k] for k in range(2)]
            for j in range(i+2,len(p)):
                if i==0 and j==len(p)-1:continue
                c=p[j];d=p[(j+1)%len(p)];v=[d[k]-c[k] for k in range(2)]
                det=u[0]*v[1]-u[1]*v[0]
                if abs(det)<1e-10:continue
                delta=[c[k]-a[k] for k in range(2)]
                t=(delta[0]*v[1]-delta[1]*v[0])/det;s=(delta[0]*u[1]-delta[1]*u[0])/det
                if 0<=t<1 and 0<=s<1:
                    dz=a[2]+t*(b[2]-a[2])-c[2]-s*(d[2]-c[2])
                    self.assertGreater(abs(dz),1)
                    events.extend([(i+t,dz>0),(j+s,dz<0)]);count+=1
        self.assertEqual(count,3)
        order=[value for _,value in sorted(events)]
        self.assertTrue(all(order[i]!=order[(i+1)%6] for i in range(6)))


if __name__=='__main__':unittest.main()
