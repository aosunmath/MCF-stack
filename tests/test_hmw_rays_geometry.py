"""Verify the drawing's topology and ray avoidance, not the shrinker PDE."""
from collections import Counter
import json
import math
from pathlib import Path
import unittest

ASSETS=Path(__file__).resolve().parents[1]/'site/assets/solitons'
COUNTS={'tetrahedron':4,'cube':6,'octahedron':8,'dodecahedron':12,'icosahedron':20,
        'polygon-3':3,'polygon-5':5,'polygon-7':7,'polygon-12':12}

def connected(graph):
    seen=set();pending=[next(iter(graph))]
    while pending:
        u=pending.pop()
        if u not in seen:seen.add(u);pending.extend(graph[u]-seen)
    return len(seen)==len(graph)

def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))

class HMWRaysTests(unittest.TestCase):
    def test_manifold_genus_and_rays(self):
        for case,count in COUNTS.items():
            with self.subTest(case=case):
                suffix='' if case=='cube' else '-'+case
                data=json.loads((ASSETS/('hmw-platonic-polygon'+suffix+'.json')).read_text())
                vertices,faces=data['vertices'],data['faces']
                self.assertEqual(data['status'],'schematic')
                self.assertEqual(data['rayCount'],count)
                self.assertEqual(data['genus'],count-1)
                edges=Counter();directions=Counter();adj={i:set() for i in range(len(vertices))}
                links=[{} for _ in vertices]
                triangles=[]
                for a,b,c in faces:
                    self.assertEqual(len({a,b,c}),3)
                    for u,v,w in [(a,b,c),(b,c,a),(c,a,b)]:
                        edge=tuple(sorted((u,v)));edges[edge]+=1;directions[edge]+=1 if u<v else -1
                        adj[u].add(v);adj[v].add(u)
                        links[u].setdefault(v,set()).add(w);links[u].setdefault(w,set()).add(v)
                    origin=vertices[a];e1=sub(vertices[b],origin);e2=sub(vertices[c],origin)
                    triangles.append((origin,e1,e2))
                self.assertEqual(set(edges.values()),{2})
                self.assertTrue(all(d==0 for d in directions.values()))
                self.assertTrue(connected(adj))
                for link in links:
                    self.assertTrue(all(len(v)==2 for v in link.values()))
                    self.assertTrue(connected(link))
                self.assertEqual(len(vertices)-len(edges)+len(faces),4-2*count)
                self.assertEqual(len(data['normals']),len(vertices))
                self.assertEqual(len(data['vertexGroups']),len(vertices))
                self.assertEqual(len(data['faceGroups']),len(faces))
                self.assertTrue(all(abs(math.hypot(*n)-1)<2e-6 for n in data['normals']))
                # Moller–Trumbore intersection test, including triangle edges.
                for ray in data['rays']:
                    self.assertAlmostEqual(math.hypot(*ray),1,places=8)
                    for a,e1,e2 in triangles:
                        p=cross(ray,e2);det=dot(e1,p)
                        if abs(det)<1e-12:continue
                        tvec=tuple(-x for x in a);u=dot(tvec,p)/det
                        if not -1e-9<=u<=1+1e-9:continue
                        q=cross(tvec,e1);v=dot(ray,q)/det
                        if v<-1e-9 or u+v>1+1e-9:continue
                        self.assertLessEqual(dot(e2,q)/det,0,'A prescribed ray meets the surface')

    def test_compact_model_does_not_change_theorem_properties(self):
        root=ASSETS.parents[2]
        entries=json.loads((root/'catalogue-properties.json').read_text())['examples']
        item=next(x for x in entries if x['label']=='ex:catalogue-hmw-platonic-polygon')
        self.assertEqual([c['compact'] for c in item['cases']],[None,None,False])
        audit=json.loads((ASSETS/'hmw-rays-audit.json').read_text())
        self.assertFalse(audit['pde_solved'])
        self.assertEqual(set(audit['models']),set(COUNTS))

if __name__=='__main__':unittest.main()
