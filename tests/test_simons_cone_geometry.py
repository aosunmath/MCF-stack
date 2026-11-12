import json
from pathlib import Path
import sys
import unittest
import math
try:
    import numpy as np
    import scipy
except ImportError:
    np = None

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
if np is not None:
    from generate_simons_cone import minimal_profile, operator, pde_run


class SimonsConeGeometryTests(unittest.TestCase):
    @unittest.skipIf(np is None, 'Optional numerical regeneration needs NumPy and SciPy')
    def test_ode_axis_asymptote_and_opposite_curvatures(self):
        for p,q in [(4,4),(5,5),(3,5)]:
            r=np.linspace(0,30,3001)
            u,d=minimal_profile(p,q)(r)
            self.assertEqual(u[0],1)
            self.assertEqual(d[0],0)
            self.assertTrue(np.all(u>np.sqrt((q-1)/(p-1))*r))
            self.assertTrue(np.all(np.diff(d)>0))
            # Check the independently differenced derivative against the minimal equation.
            dd=np.gradient(d,r,edge_order=2)
            defect=dd[10:-10]/(1+d[10:-10]**2)+(p-1)*d[10:-10]/r[10:-10]-(q-1)/u[10:-10]
            self.assertLess(np.max(abs(defect)),1e-4)
            self.assertLess(abs(d[-1]-np.sqrt((q-1)/(p-1))),.001)

    @unittest.skipIf(np is None, 'Optional numerical regeneration needs NumPy and SciPy')
    def test_operator_on_exact_cylinder_and_sphere(self):
        r=2*np.linspace(0,1,401)**2
        self.assertTrue(np.allclose(operator(r,np.full_like(r,3.)), -1.,atol=1e-5))
        sphere=np.sqrt(16-r*r)
        self.assertLess(np.max(abs(operator(r,sphere)+7/sphere[:-1])),1e-4)

    @unittest.skipIf(np is None, 'Optional numerical regeneration needs NumPy and SciPy')
    def test_stationary_minimal_leaf_drift(self):
        r,t,u,_=pde_run(n=240,rounding=1,amplitude=0,end=.02)
        self.assertLess(np.max(abs(u[-1]-u[0])),3e-6)

    def test_saved_refinement_and_source_restrictions(self):
        data=json.loads((ROOT/'site/assets/solitons/simons-cone-experiment.json').read_text())
        a=data['audit']
        errors=a['stationary_leaf_residuals_120_240_480']
        self.assertTrue(all(3.8<errors[i]/errors[i+1]<4.2 for i in range(2)))
        self.assertLess(a['grid_240_480_max_error_all_times'],4e-4)
        self.assertLess(a['domain_5_7_max_error_r_le_2'],5e-5)
        self.assertLess(a['rounding_001_0005_final_max_error'],2e-6)
        self.assertTrue(all(math.isfinite(v) for row in data['pde']['values'] for v in row))
        self.assertGreater(min(data['pde']['axis']),0)
        for item in data['profiles']:
            self.assertLess(item['refinement_error'],1e-6)
        text=(ROOT/'content/gmt-foundations/catalogue-simons-cones.tex').read_text()
        self.assertIn('N=8:\\ \\ell\\geq4',text)
        self.assertIn('N\\geq9:\\ \\ell\\geq3',text)


if __name__=='__main__':unittest.main()
