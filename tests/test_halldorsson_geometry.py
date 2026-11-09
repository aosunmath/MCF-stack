"""Check source normalization, sampled immersions and safe sandbox packaging."""
import cmath
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/solitons'

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return [x-y for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def scale(a,k):return [x*k for x in a]

def minimal(u,p,h,a):
    z=(h*math.sinh(h*u)+1j*a*math.cosh(h*u))*cmath.exp(1j*(p-a*u))
    return [z.real,z.imag,h*p]

class HalldorssonGeometryTests(unittest.TestCase):
    def test_minimal_formula_has_zero_mean_curvature_for_both_cases(self):
        # Differentiate the actual immersion independently of the source ODE.
        e=1e-4
        for h,a in [(1,0),(1,1),(.5,1)]:
            for u,p in [(.2,.3),(1.1,-.7)]:
                f=lambda x,y:minimal(x,y,h,a)
                c=f(u,p);fu=scale(sub(f(u+e,p),f(u-e,p)),1/(2*e));fv=scale(sub(f(u,p+e),f(u,p-e)),1/(2*e))
                fuu=scale([x+y-2*z for x,y,z in zip(f(u+e,p),f(u-e,p),c)],1/e**2)
                fvv=scale([x+y-2*z for x,y,z in zip(f(u,p+e),f(u,p-e),c)],1/e**2)
                fuv=scale([w-x-y+z for w,x,y,z in zip(f(u+e,p+e),f(u+e,p-e),f(u-e,p+e),f(u-e,p-e))],1/(4*e**2))
                normal=cross(fu,fv);normal=scale(normal,1/math.sqrt(dot(normal,normal)))
                E,F,G=dot(fu,fu),dot(fu,fv),dot(fv,fv)
                mean=(G*dot(fuu,normal)-2*F*dot(fuv,normal)+E*dot(fvv,normal))/(E*G-F*F)
                self.assertLess(abs(mean),2e-6)

    def test_all_windows_are_finite_and_inline_viewers_work_without_fetch(self):
        runtime=(ROOT/'site/assets/halldorsson-viewer.mjs').read_text()
        self.assertNotIn('fetch(',runtime)
        for path in OUT.glob('halldorsson-*.json'):
            if path.name=='halldorsson-audit.json':continue
            data=json.loads(path.read_text())
            page=(ROOT/'site/experiments'/path.with_suffix('.html').name).read_text()
            selected_runtime = ((ROOT/'site/assets/annulus-shrinker-viewer.mjs').read_text()
                                if path.stem=='halldorsson-dense' else runtime)
            self.assertIn(selected_runtime,page)
            self.assertIn('id="geometry"',page)
            for variant in data['variants']:
                vertices=variant['vertices'];self.assertGreater(len(vertices),100)
                self.assertTrue(all(len(p)==3 and all(math.isfinite(x) for x in p) for p in vertices))
                self.assertTrue(all(0<=i<len(vertices) for f in variant['faces']+variant['paths'] for i in f))
                self.assertTrue(variant['note'])

    def test_numerical_diagnostics_and_nonproper_metadata(self):
        audit=json.loads((OUT/'halldorsson-audit.json').read_text())['checks']
        self.assertLess(abs(audit['dense_shooting']['turning_residual']),1e-9)
        for item in audit.values():
            if 'refinement_max' in item:self.assertLess(item['refinement_max'],1e-7)
            if 'unit_tangent_difference' in item:self.assertLess(item['unit_tangent_difference'],.006)
            if 'mean_curvature_translator_residual' in item:self.assertLess(item['mean_curvature_translator_residual'],1e-10)
        props=json.loads((ROOT/'catalogue-properties.json').read_text())['examples']
        for name in ['halldorsson-dense-shrinkers','rotating-shrinking-curves']:
            record=next(r for r in props if r['label']=='ex:catalogue-'+name)
            for case in record['cases']:
                self.assertFalse(case['compact']);self.assertEqual(case['ends']['key'],'2')
                for q in ['gaussian','entropy']:
                    self.assertEqual(case[q]['status'],'exact');self.assertIn('∞',case[q]['text']);self.assertNotIn('value',case[q])

if __name__=='__main__':unittest.main()
