"""Independent geometric checks for illustrative assets, not existence proofs."""
import json
import math
from pathlib import Path
import unittest
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'site/assets/solitons'

def model(name):return json.loads((ASSETS/(name+'.json')).read_text())

class SolitonGeometryTests(unittest.TestCase):
    def test_moller_limit_uses_the_numerical_torus_and_source_intersection_bounds(self):
        data=model('moller-gluing')
        self.assertEqual(data['kind'],'moller-configuration')
        self.assertEqual(data['status'],'numerical-limiting-configuration')
        # Read the original export independently of the new generator.
        source=model('angenent-torus')
        row=source['faces'][0][1]
        expected=[[math.hypot(*p[:2]),p[2]] for p in source['vertices'][::row]]
        self.assertEqual(data['meridians'][1],expected)
        for p in data['intersections']:
            self.assertAlmostEqual(p['r']**2+p['z']**2,4,places=12)
            self.assertLess(math.hypot(abs(p['z'])-29/32,p['r']-41/23),.005)
        lower,upper=data['intersections']
        self.assertAlmostEqual(lower['z'],-upper['z'],places=12)
        self.assertAlmostEqual(lower['r'],upper['r'],places=12)
        for ring,point in zip(data['paths'],data['intersections']):
            self.assertEqual(ring[0],ring[-1])
            for index in ring:
                x,y,z=data['vertices'][index]
                self.assertAlmostEqual(z,point['z'],places=7)
                self.assertAlmostEqual(math.hypot(x,y),point['r'],places=7)
        sphere_indices={j for face,group in zip(data['faces'],data['faceGroups']) if group==0 for j in face}
        for j in sphere_indices:
            self.assertAlmostEqual(sum(x*x for x in data['vertices'][j]),4,places=7)

    def test_drugan_mesh_has_spherical_domain_and_reflection_symmetry(self):
        data=model('drugan-sphere')
        self.assertEqual(data['status'],'numerical-ode')
        v,f=data['vertices'],data['faces']
        edges=Counter(tuple(sorted((face[i],face[(i+1)%3]))) for face in f for i in range(3))
        self.assertEqual(set(edges.values()),{2})
        self.assertEqual(len(v)-len(edges)+len(f),2)
        for face in f:
            self.assertEqual(len(set(face)),3)
        p=data['revolution']['meridian']
        self.assertEqual(p[0][0],0)
        self.assertEqual(p[-1][0],0)
        self.assertTrue(all(r>0 for r,z in p[1:-1]))
        for (r,z),(rr,zz) in zip(p,reversed(p)):
            self.assertAlmostEqual(r,rr,places=8)
            self.assertAlmostEqual(z,-zz,places=8)
        # The first graph crosses z=0 before its maximum radius. Its reflection
        # therefore meets it away from the smooth inner reflection join.
        half=p[:len(p)//2+1]
        maximum=max(range(len(half)),key=lambda i:half[i][0])
        self.assertTrue(any(a[1]>0>b[1] and a[0]>2 for a,b in zip(half[:maximum],half[1:maximum+1])))

    def test_drugan_export_satisfies_arc_length_ode_independently(self):
        d=model('drugan-sphere')['shooting']
        states,arc=d['states'],d['arc']
        errors=[]
        for i in range(2,len(states)-2):
            r,z,a=states[i]
            # Fourth-order difference quotient, independent of solver RHS calls.
            h=(arc[i+1]-arc[i-1])/2
            derivative=[(states[i-2][j]-8*states[i-1][j]+8*states[i+1][j]-states[i+2][j])/(12*h) for j in range(3)]
            expected=[math.cos(a),math.sin(a),(r/2-1/r)*math.sin(a)-z/2*math.cos(a)]
            errors.extend(abs(x-y) for x,y in zip(derivative,expected))
        self.assertLess(max(errors),2e-6)
        audit=json.loads((ASSETS/'drugan-audit.json').read_text())
        self.assertLess(audit['reflection_height_residual'],1e-10)
        self.assertLess(audit['reflection_angle_residual'],1e-10)
        self.assertLess(audit['refinement']['pole_height_change'],1e-9)
        self.assertLess(audit['refinement']['reflection_radius_change'],1e-9)
        self.assertLess(audit['refinement']['aligned_profile_max_component_change'],1e-9)
        self.assertTrue(.39<audit['pole_height']<.40)
        self.assertTrue(.83<audit['reflection_radius']<.84)

    def test_round_shrinker_normalization_and_clifford_dimension(self):
        for p in model('sphere')['vertices']:
            self.assertAlmostEqual(sum(x*x for x in p),4,places=5)
        for x,y,z in model('cylinder')['vertices']:
            self.assertAlmostEqual(x*x+y*y,2,places=5)
        for p in model('clifford')['vertices']:
            self.assertEqual(len(p),4)
            self.assertAlmostEqual(p[0]**2+p[1]**2,2,places=5)
            self.assertAlmostEqual(p[2]**2+p[3]**2,2,places=5)

    def test_grim_and_catenoid_assets_match_the_stated_formulas(self):
        for name,a in [('grim-reaper',0),('tilted-grim',.65)]:
            A=1+a*a
            for x,y,z in model(name)['vertices']:
                self.assertLess(abs(z+A*math.log(math.cos(x/math.sqrt(A)))-a*y),2e-6)
        for x,y,z in model('catenoid')['vertices']:
            self.assertLess(abs(math.hypot(x,y)-math.cosh(z)),1e-6)

    def test_numerical_closure_and_source_status_are_explicit(self):
        audit=json.loads((ASSETS/'geometry-audit.json').read_text())
        self.assertLess(audit['angenent-torus']['return_angle_error'],1e-7)
        self.assertLess(audit['angenent-torus']['return_position_error'],1e-7)
        self.assertTrue(3.30<audit['angenent-torus']['outer_radius']<3.33)
        self.assertLess(audit['abresch-langer']['closure_error'],1e-7)
        for name in ['bowl','angenent-torus','abresch-langer','expanding-graph','one-sheet-expander']:
            self.assertEqual(model(name)['status'],'numerical-ode')
        # A flat quadratic graph would have f(5)=6.25, and is not the exact bowl.
        bowl=model('bowl')['vertices']
        heights=[z for x,y,z in bowl if abs(math.hypot(x,y)-5)<1e-6]
        self.assertTrue(heights)
        self.assertGreater(abs(heights[0]-6.25),1)

if __name__=='__main__':unittest.main()
