"""Independent checks on the displayed numerical translator, not a proof."""
from collections import Counter
import json
import math
from pathlib import Path
import unittest

ASSETS=Path(__file__).resolve().parents[1]/'site/assets/solitons'

class DeltaWingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ASSETS/'delta-wing.json').read_text())

    def test_height_cut_is_one_oriented_disk_with_no_capped_rim(self):
        data=self.data;v=data['vertices'];faces=data['faces'];edges=Counter();direction=Counter()
        for a,b,c in faces:
            p,q,r=v[a],v[b],v[c]
            self.assertGreater((q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]),0)
            for i,j in [(a,b),(b,c),(c,a)]:
                edge=tuple(sorted((i,j)));edges[edge]+=1;direction[edge]+=1 if i<j else -1
        self.assertEqual(len(v)-len(edges)+len(faces),1)
        self.assertEqual(set(edges.values()),{1,2})
        rim=[edge for edge,count in edges.items() if count==1]
        self.assertEqual(len(rim),192)
        self.assertTrue(all(abs(v[i][2]-6)<1e-7 for edge in rim for i in edge))
        self.assertTrue(all(direction[e]==0 for e,count in edges.items() if count==2))
        self.assertTrue(all(abs(y)<data['halfWidth'] for x,y,z in v))
        self.assertTrue(all(n[2]>0 and abs(math.hypot(*n)-1)<1e-7 for n in data['normals']))

    def test_apex_obeys_unit_speed_and_both_reflection_symmetries(self):
        d=self.data
        self.assertEqual(d['status'],'numerical-pde')
        self.assertAlmostEqual(2*d['halfWidth'],math.sqrt(2)*math.pi)
        self.assertEqual(d['vertices'][0],[0,0,0])
        line=d['longitudinal'];section=d['sections'][0]
        def apex_second(points):
            mid=len(points)//2;h=points[mid+1][0]-points[mid][0]
            self.assertEqual(points[mid][1],0)
            for a,b in zip(points,reversed(points)):
                self.assertAlmostEqual(a[0],-b[0],places=7);self.assertAlmostEqual(a[1],b[1],places=7)
            return (points[mid+1][1]+points[mid-1][1])/(h*h)
        a,b=apex_second(line),apex_second(section)
        self.assertGreater(a,0);self.assertGreater(b,0)
        self.assertAlmostEqual(a+b,1,delta=.002)

if __name__=='__main__':unittest.main()
