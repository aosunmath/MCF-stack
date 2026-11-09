"""Checks on the displayed three-dimensional representatives, not a proof."""
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'site/assets/solitons'


class ApexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ASSETS/'apex-ellipsoid.json').read_text())

    def test_three_patches_have_oriented_disk_topology_and_unit_normals(self):
        for d in [self.data,*self.data['cases'].values()]:
            v=d['vertices'];edges=Counter();directions=Counter()
            for a,b,c in d['faces']:
                p,q,r=v[a],v[b],v[c]
                self.assertGreater((q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]),0)
                for i,j in [(a,b),(b,c),(c,a)]:
                    e=tuple(sorted((i,j)));edges[e]+=1;directions[e]+=1 if i<j else -1
            self.assertEqual(len(v)-len(edges)+len(d['faces']),1)
            self.assertEqual(set(edges.values()),{1,2})
            self.assertTrue(all(directions[e]==0 for e,count in edges.items() if count==2))
            self.assertTrue(all(n[2]>0 and abs(math.hypot(*n)-1)<2e-7 for n in d['normals']))
            self.assertAlmostEqual(sum(d['curvatures']),1,delta=1e-6)
            self.assertTrue(any(math.hypot(*p)<1e-7 for p in v))
            self.assertTrue(all(-1e-7<=p[2]<=6+1e-7 for p in v))

    def test_grim_is_exact_formula_with_a_minimum_line(self):
        g=self.data['cases']['grim']
        for x,y,z in g['vertices']:
            self.assertLess(abs(y),math.pi/2)
            self.assertAlmostEqual(z,-math.log(math.cos(y)),delta=3e-6)
        self.assertEqual(g['curvatures'],[0,1])
        self.assertGreater(sum(abs(p[2])<1e-8 for p in g['vertices']),50)

    def test_wing_reuses_the_audited_pde_geometry(self):
        old=json.loads((ASSETS/'delta-wing.json').read_text())
        for k in ['vertices','normals','faces','paths']:
            self.assertEqual(self.data[k],old[k])
        audit=json.loads((ASSETS/'apex-audit.json').read_text())
        self.assertEqual(audit['delta_wing']['sha256'],hashlib.sha256((ASSETS/'delta-wing.json').read_bytes()).hexdigest())

    def test_sections_encode_the_claimed_apex_data(self):
        for d in [self.data,*self.data['cases'].values()]:
            for i,p in enumerate(d['profiles']):
                mid=len(p)//2;h=p[mid+1][0]-p[mid][0]
                self.assertAlmostEqual(p[mid][1],0,places=7)
                self.assertAlmostEqual((p[mid+1][1]+p[mid-1][1])/h**2,d['curvatures'][i],delta=.002)
                for a,b in zip(p,reversed(p)):
                    self.assertAlmostEqual(a[0],-b[0],places=7);self.assertAlmostEqual(a[1],b[1],places=7)
        self.assertEqual(self.data['cases']['bowl']['profiles'][0],self.data['cases']['bowl']['profiles'][1])

    def test_old_generator_preserves_reviewed_drawing(self):
        path=ROOT/'scripts/generate_translator_schematics.py'
        spec=importlib.util.spec_from_file_location('translator_schematics',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        before=(ASSETS/'apex-ellipsoid.svg').read_bytes();module.apex()
        self.assertEqual(before,(ASSETS/'apex-ellipsoid.svg').read_bytes())


if __name__=='__main__':unittest.main()
