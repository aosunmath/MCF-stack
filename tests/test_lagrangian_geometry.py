"""Independent checks of normalization and quotient topology, not existence proofs."""
from collections import Counter, defaultdict, deque
import json
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from generate_lagrangian_catalogue import mobius, rotating, seed_gradient


def dot(a,b):return sum(x*y for x,y in zip(a,b))
def plus(a,b,scale=1):return [x+scale*y for x,y in zip(a,b)]
def scaled(a,k):return [k*x for x in a]


def geometry(f,u,v,h=2e-4):
    p=f(u,v);up=f(u+h,v);um=f(u-h,v);vp=f(u,v+h);vm=f(u,v-h)
    a=scaled(plus(up,um,-1),1/(2*h));b=scaled(plus(vp,vm,-1),1/(2*h))
    aa=scaled(plus(plus(up,um),p,-2),1/h**2);bb=scaled(plus(plus(vp,vm),p,-2),1/h**2)
    ab=scaled(plus(plus(f(u+h,v+h),f(u-h,v-h)),plus(f(u+h,v-h),f(u-h,v+h)),-1),1/(4*h*h))
    E,F,G=dot(a,a),dot(a,b),dot(b,b);det=E*G-F*F
    def normal(w):
        wa,wb=dot(w,a),dot(w,b)
        return plus(plus(w,a,-(G*wa-F*wb)/det),b,-(E*wb-F*wa)/det)
    H=normal(scaled(plus(plus(scaled(aa,G),scaled(ab,-2*F)),scaled(bb,E)),1/det))
    omega=sum(a[i]*b[i+1]-a[i+1]*b[i] for i in (0,2))
    return p,H,normal,omega


def geometry3(f,point,h=2e-4):
    """Trace the normal Hessian using the numerically induced 3x3 metric."""
    def at(i,di,j=0,dj=0):
        q=list(point);q[i]+=di;q[j]+=dj
        return f(*q)
    p=f(*point)
    tangent=[scaled(plus(at(i,h),at(i,-h),-1),1/(2*h)) for i in range(3)]
    matrix=[[dot(a,b) for b in tangent]+[int(i==j) for j in range(3)] for i,a in enumerate(tangent)]
    for i in range(3):
        pivot=matrix[i][i];matrix[i]=[v/pivot for v in matrix[i]]
        for j in range(3):
            if j!=i:
                coefficient=matrix[j][i];matrix[j]=[a-coefficient*b for a,b in zip(matrix[j],matrix[i])]
    inverse=[row[3:] for row in matrix]
    def normal(v):
        result=list(v)
        for i in range(3):result=plus(result,tangent[i],-sum(inverse[i][j]*dot(v,tangent[j]) for j in range(3)))
        return result
    trace=[0.0]*6
    for i in range(3):
        for j in range(3):
            if i==j:second=scaled(plus(plus(at(i,h),at(i,-h)),p,-2),1/h**2)
            else:second=scaled(plus(plus(at(i,h,j,h),at(i,-h,j,-h)),plus(at(i,h,j,-h),at(i,-h,j,h)),-1),1/(4*h*h))
            trace=plus(trace,second,inverse[i][j])
    omega=max(abs(sum(tangent[i][a]*tangent[j][a+1]-tangent[i][a+1]*tangent[j][a] for a in (0,2,4))) for i in range(3) for j in range(3))
    return p,normal(trace),normal,omega


class LagrangianGeometryTests(unittest.TestCase):
    def test_quadric_normalizations_and_stationary_profile_product(self):
        def coordinates(z):return [a for v in z for a in (v.real,v.imag)]
        def quadric(theta,r,s,expanding=False):
            radius=r if expanding else math.sqrt(2+r*r)
            height=math.sqrt(2+r*r) if expanding else r
            phase=complex(math.cos(s),math.sin(s))
            return coordinates([radius*math.cos(theta)*phase,radius*math.sin(theta)*phase,height*phase.conjugate()])
        def stationary(theta,x,y):
            def profile(s):return complex(math.cos(s),math.sin(s))/math.sqrt(math.cos(2*s))
            def primitive(s):return math.log(1/math.cos(2*s)+math.tan(2*s))/2
            a,b=profile(x),profile(y)
            return coordinates([a*b*math.cos(theta),a*b*math.sin(theta),complex((abs(b)**2-abs(a)**2)/2,primitive(y)-primitive(x))])
        for f,point,scale in [(quadric,(.7,.6,.3),-.5),(lambda a,b,c:quadric(a,b,c,True),(.4,.9,.2),.5),(stationary,(.8,.2,-.3),0)]:
            p,H,normal,omega=geometry3(f,point)
            self.assertLess(max(abs(a-b) for a,b in zip(H,scaled(normal(p),scale))),3e-6)
            self.assertLess(omega,3e-6)

    def test_exact_maps_satisfy_their_lagrangian_and_soliton_equations(self):
        for f,points,kind in [(mobius,[(.2,-.7),(1.2,.4),(2.1,0)],'shrinker'),
                              (rotating,[(.4,-.8),(1.3,1.1),(0,.3)],'translator')]:
            for u,v in points:
                p,H,normal,omega=geometry(f,u,v)
                target=scaled(normal(p),-.5) if kind=='shrinker' else normal([0,0,1,0])
                self.assertLess(max(abs(x-y) for x,y in zip(H,target)),2e-6)
                self.assertLess(abs(omega),2e-6)

    def test_mobius_mesh_has_a_twisted_seam_and_one_boundary_component(self):
        d=json.loads((ROOT/'site/assets/solitons/mobius-shrinker.json').read_text())
        edges=Counter();adj=defaultdict(set)
        for face in d['faces']:
            for i,j in zip(face,face[1:]+face[:1]):edges[tuple(sorted((i,j)))]+=1
        self.assertEqual(len(d['vertices'])-len(edges)+len(d['faces']),0)
        for (i,j),count in edges.items():
            self.assertIn(count,(1,2))
            if count==1:adj[i].add(j);adj[j].add(i)
        self.assertTrue(adj)
        self.assertTrue(all(len(v)==2 for v in adj.values()))
        seen=set();q=deque([next(iter(adj))])
        while q:
            i=q.popleft()
            if i in seen:continue
            seen.add(i);q.extend(adj[i]-seen)
        self.assertEqual(len(seen),len(adj))
        for theta,r in [(.3,.6),(1.8,-.9)]:
            self.assertLess(max(abs(a-b) for a,b in zip(mobius(theta,r),mobius(theta+math.pi,-r))),1e-12)

    def test_initial_seed_is_homogeneous_and_strictly_two_convex_but_nonconvex(self):
        for theta in [i*math.tau/151 for i in range(151)]:
            x,y=math.cos(theta),math.sin(theta);h=1e-4
            a=seed_gradient(x+h,y);b=seed_gradient(x-h,y)
            c=seed_gradient(x,y+h);d=seed_gradient(x,y-h)
            xx=(a[1]-b[1])/(2*h);yy=(c[3]-d[3])/(2*h);xy=(c[1]-d[1])/(2*h)
            discriminant=math.sqrt((xx-yy)**2+4*xy*xy)
            low,high=(xx+yy-discriminant)/2,(xx+yy+discriminant)/2
            self.assertLess(low,0);self.assertGreater(low+high,0);self.assertGreater(1+low*high,0)
            self.assertLess(abs(low+.1),.0038);self.assertLess(abs(high-.5),.0038)
            self.assertLess(max(abs(a-3*b) for a,b in zip(seed_gradient(3*x,3*y),seed_gradient(x,y))),1e-12)


if __name__=='__main__':unittest.main()
