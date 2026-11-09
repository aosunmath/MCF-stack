"""Independent finite-difference checks of the exported network geometry."""
import json
import math
from pathlib import Path
import unittest

ASSETS=Path(__file__).resolve().parents[1]/'site/assets/solitons'


class ExpandingNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ASSETS/'expanding-network.json').read_text())
        cls.vertices=cls.data['vertices']
        cls.arms=[[cls.vertices[i][:2] for i in path] for path in cls.data['paths'][:4]]

    def test_curvature_equation_from_positions(self):
        # Five-point differences, independent of the integrated theta variable.
        h=self.data['audit']['export_arclength_step']
        for arm in self.arms:
            for i in range(2,700,7):
                velocity=[sum(c*arm[i+j][k] for c,j in [(1,-2),(-8,-1),(8,1),(-1,2)])/(12*h) for k in range(2)]
                acceleration=[sum(c*arm[i+j][k] for c,j in [(-1,-2),(16,-1),(-30,0),(16,1),(-1,2)])/(12*h*h) for k in range(2)]
                speed=math.hypot(*velocity);t=[v/speed for v in velocity]
                p=arm[i];at=sum(a*b for a,b in zip(acceleration,t));pt=sum(a*b for a,b in zip(p,t))
                curvature=[(acceleration[k]-at*t[k])/speed**2 for k in range(2)]
                expected=[(p[k]-pt*t[k])/2 for k in range(2)]
                self.assertLess(math.dist(curvature,expected),5e-7)
                self.assertAlmostEqual(speed,1,places=7)

    def test_balanced_junctions_and_tree_embedding(self):
        a=self.data['junction'];h=.01
        for arm,sx,sy in zip(self.arms,[1,-1,-1,1],[1,1,-1,-1]):
            self.assertLess(math.dist(arm[0],[sx*a,0]),1e-10)
            tangent=[sum(c*arm[j][k] for c,j in [(-25,0),(48,1),(-36,2),(16,3),(-3,4)])/(12*h) for k in range(2)]
            self.assertLess(math.dist(tangent,[sx*.5,sy*math.sqrt(3)/2]),1e-7)
            for p,q in zip(arm,arm[1:]):
                self.assertGreater(sx*q[0],sx*p[0])
                self.assertGreater(sy*q[1],sy*p[1])
            self.assertLess(abs(arm[-1][0]*sx-arm[-1][1]*sy),1e-8)
        # After identifying shared endpoints, five edges and six vertices form a tree.
        center=[self.vertices[i] for i in self.data['paths'][4]]
        self.assertEqual(center,[[-a,0,0],[a,0,0]])
        self.assertEqual(len(self.data['paths']),5)

    def test_shooting_consistency_and_positive_time_geometry(self):
        audit=self.data['audit']
        for key in ['step_halving_junction_difference','cutoff_extension_junction_difference',
                    'endpoint_tangent_angle_error','endpoint_distance_to_prescribed_ray',
                    'step_halving_max_position_difference']:
            self.assertLess(audit[key],1e-10)
        self.assertGreater(self.data['junction'],0)
        self.assertEqual(self.data['status'],'numerical-ode')


if __name__=='__main__':unittest.main()
