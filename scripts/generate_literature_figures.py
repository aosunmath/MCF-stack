"""Source-informed flow plates and interactive geometry for the literature additions.

Optional regeneration dependencies: numpy and scipy. No source PDFs are exported.
Numerical ODE profiles are sampled, not certified global existence proofs. Schematic
families are deliberately represented by orbit/limit diagrams, with that status visible.
"""
from pathlib import Path
import json, math, html
import numpy as np
from scipy.integrate import solve_ivp, cumulative_trapezoid
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/solitons'
TAU=2*np.pi
AUDIT={}
COLORS=['#087f8c','#c56535','#6d55a1','#88939d']

def geom():return dict(vertices=[],faces=[],paths=[],pathColors=[],faceColors=[])
def path(g,pts,color=0):
    start=len(g['vertices']);a=np.asarray(pts,float)
    if a.shape[1]==2:a=np.column_stack([a,np.zeros(len(a))])
    g['vertices'].extend(a.tolist());g['paths'].append(list(range(start,start+len(a))));g['pathColors'].append(color)
def mesh(g,fn,us,vs,color=0):
    start=len(g['vertices']);nu,nv=len(us),len(vs)
    g['vertices'].extend([list(fn(u,v)) for u in us for v in vs])
    for i in range(nu-1):
        for j in range(nv-1):
            a=start+i*nv+j;g['faces'].append([a,a+nv,a+nv+1,a+1]);g['faceColors'].append(color)
    for i in np.linspace(0,nu-1,5).astype(int):g['paths'].append([start+i*nv+j for j in range(nv)]);g['pathColors'].append(color)
    for j in np.linspace(0,nv-1,5).astype(int):g['paths'].append([start+i*nv+j for i in range(nu)]);g['pathColors'].append(color)
def line(g,a,b,color=3):path(g,[a,b],color)
def circle(g,r=1,center=(0,0),color=3):path(g,[[center[0]+r*np.cos(a),center[1]+r*np.sin(a),0] for a in np.linspace(0,TAU,161)],color)
def revolve(g,profile,color=0):
    p=np.asarray(profile)
    mesh(g,lambda i,a:(p[int(i),0]*np.cos(a),p[int(i),0]*np.sin(a),p[int(i),1]),np.arange(len(p)),np.linspace(0,TAU,33),color)
def transform(g,fn):
    out={**g,'vertices':[list(fn(np.array(v))) for v in g['vertices']]};return out

def ode(fun,y0,end=10,steps=240):
    sol=solve_ivp(fun,[0,end],y0,rtol=2e-10,atol=2e-11,max_step=.025,dense_output=True)
    if not sol.success:raise ValueError(sol.message)
    return sol.sol(np.linspace(0,end,steps)).T

def anciaux(n=3,lam=.5,closed=True):
    def f(s,Y):r,p,a=Y;return [np.cos(a),np.sin(a)/r,(lam*r-n/r)*np.sin(a)]
    if lam<0:
        Y=ode(f,[1,0,np.pi/2],7,180);Z=ode(f,[1,0,np.pi/2],-7,180)
        out=np.vstack([Z[::-1],Y[1:]])
    else:
        def cycle(a,ret=False):
            def ev(s,Y):return np.cos(Y[2])
            ev.direction=1;ev.terminal=True
            start=ode(f,[a,0,np.pi/2],1e-5,2)[-1]
            so=solve_ivp(f,[1e-5,60],start,events=ev,rtol=2e-10,atol=2e-11,max_step=.025,dense_output=True)
            return so if ret else so.y[1,-1]-TAU/3
        a=brentq(cycle,.02,np.sqrt(n/lam)*.99,xtol=1e-10)
        period=cycle(a,True).t[-1]
        out=ode(f,[a,0,np.pi/2],period*3,600)
        AUDIT[f'anciaux-{n}-{lam}']={'phase_closure_error':float(abs(cycle(a))*3),'radius':float(a),'period':float(period)}
    z=out[:,0]*np.exp(1j*out[:,1]);return z,out

def network(k,sign):
    def f(s,Y):x,y,b=Y;return [np.cos(b),np.sin(b),sign*(-x*np.sin(b)+y*np.cos(b))/2]
    def shoot(a,ret=False):
        def ev(s,Y):return Y[1] if k==1 else np.arctan2(Y[1],Y[0])-np.pi/k
        ev.terminal=True;ev.direction=-1 if k==1 else 1
        so=solve_ivp(f,[0,30],[a,0,2*np.pi/3],events=ev,rtol=2e-10,atol=2e-11,max_step=.015,dense_output=True)
        if not so.t_events[0].size:raise ValueError('Network event not reached')
        return so if ret else so.y[2,-1]-(3*np.pi/2 if k==1 else np.pi/k+np.pi/2)
    a=brentq(shoot,.05,2,xtol=1e-10);so=shoot(a,True);half=so.sol(np.linspace(0,so.t[-1],100))[:2].T
    z=half[:,0]+1j*half[:,1];arc=np.r_[z, (np.exp(2j*np.pi/k)*np.conj(z))[::-1][1:]]
    g=geom()
    for j in range(k):
        zz=arc*np.exp(1j*TAU*j/k);path(g,np.c_[zz.real,zz.imag])
        ray=np.exp(1j*TAU*j/k)*np.array([a,3.5]);path(g,np.c_[ray.real,ray.imag],1)
    AUDIT[f'network-{k}-{sign}']={'shooting_angle_error':float(abs(shoot(a))),'junction_radius':float(a),'junction_angle_degrees':120}
    return g

def graph_flow():
    def run(n):
        x=np.linspace(-8,8,n);h=x[1]-x[0];X,Y=np.meshgrid(x,x);R=np.hypot(X,Y)
        U=.35*(X*X-Y*Y)/np.maximum(R,1e-12);t=0;frames=[]
        for target in [.25,1,2.25]:
            while t<target-1e-12:
                dt=min(.15*h*h,target-t);ux=(U[1:-1,2:]-U[1:-1,:-2])/(2*h);uy=(U[2:,1:-1]-U[:-2,1:-1])/(2*h)
                xx=(U[1:-1,2:]+U[1:-1,:-2]-2*U[1:-1,1:-1])/h**2;yy=(U[2:,1:-1]+U[:-2,1:-1]-2*U[1:-1,1:-1])/h**2
                xy=(U[2:,2:]-U[2:,:-2]-U[:-2,2:]+U[:-2,:-2])/(4*h*h)
                U[1:-1,1:-1]+=dt*((1+uy*uy)*xx+(1+ux*ux)*yy-2*ux*uy*xy)/(1+ux*ux+uy*uy);t+=dt
            frames.append(U.copy())
        return x,frames
    x,us=run(81);xx,fine=run(161);errs=[float(np.max(abs(a[20:61,20:61]-b[40:121:2,40:121:2]))) for a,b in zip(us,fine)]
    AUDIT['graph-expander']={'grids':[81,161],'domain':[-8,8],'display_domain':[-4,4],'max_refinement_difference':errs,'times':[.25,1,2.25],'boundary':'fixed initial cone; finite-domain approximation'}
    result=[]
    for U in fine:
        g=geom();mesh(g,lambda i,j:(xx[int(i)],xx[int(j)],U[int(j),int(i)]),np.arange(40,121,3),np.arange(40,121,3));result.append(g)
    return result

def lens_cluster():
    def shoot(b,ret=False):
        def f(r,Y):u,v=Y;return [v,(1+v*v)*((r*v-u)/2-v/r)]
        def ev(r,Y):return Y[0]
        ev.terminal=True;ev.direction=-1
        so=solve_ivp(f,[1e-5,10],[b-b*1e-10/8,-b*1e-5/4],events=ev,rtol=1e-10,atol=1e-11,max_step=.01,dense_output=True)
        return so if ret else so.y[1,-1]+np.sqrt(3)
    b=brentq(shoot,.1,2.5);so=shoot(b,True);r=np.linspace(1e-5,so.t[-1],65);u=so.sol(r)[0];g=geom()
    revolve(g,np.c_[r,u]);revolve(g,np.c_[r,-u],1)
    mesh(g,lambda r,a:(r*np.cos(a),r*np.sin(a),0),np.linspace(r[-1],3.7,7),np.linspace(0,TAU,49),3)
    AUDIT['lens-cluster']={'slope_residual':float(abs(shoot(b))),'height':float(b),'junction_radius':float(r[-1])};return g

def base_numeric(e):
    k=e['visual']['kind'];p=e['visual']['params'];g=geom()
    if k=='network' and p.get('rays',0) in [1,2,3,4,5,7] and p.get('network') not in ['fish','rocket','cisgeminate-eye']:
        return network(p['rays'],p.get('sign',-1))
    if k=='lens-cluster':return lens_cluster()
    if k=='birotational':
        sign=p['sign']
        def f(s,Y):x,y,a=Y;return [np.cos(a),np.sin(a),-(1/x+sign*x/2)*np.sin(a)+(1/y+sign*y/2)*np.cos(a)]
        y0=[1.6,1.2,np.arctan2(1.2,1.6)+np.pi/2];Y=ode(f,y0,4.5 if sign>0 else 2,130);Z=ode(f,y0,-4.5 if sign>0 else -2,130);P=np.vstack([Z[::-1],Y[1:]])
        path(g,np.c_[P[:,:2],np.zeros(len(P))]);line(g,[0,0,0],[6,0,0]);line(g,[0,0,0],[0,6,0])
        for idx in np.linspace(0,len(P)-1,4).astype(int):
            x,y=P[idx,:2];mesh(g,lambda u,v:(x*np.cos(u),x*np.sin(u)+.38*y*np.sin(v),y*np.cos(v)),np.linspace(0,TAU,25),np.linspace(0,TAU,17),idx%3)
        return g
    if k=='anciaux':
        z,Y=anciaux(3,p['lambda']);path(g,np.c_[z.real,z.imag,np.zeros(len(z))],1)
        # A 2D slice of the 3-fold, with the second leaf coordinate fixed.
        z=z[::5];mesh(g,lambda i,u:(np.real(z[int(i)]*np.exp(1j*u))/np.sqrt(3),np.imag(z[int(i)]*np.exp(1j*u))/np.sqrt(3),np.real(z[int(i)]*np.exp(-1j*u))/np.sqrt(3)),np.arange(len(z)),np.linspace(0,TAU,33))
        return g
    if k in ['castro-pair','su-pair','su-helicoid']:
        n=1 if k=='castro-pair' else 2
        if k=='castro-pair':a=np.exp(1j*np.linspace(0,TAU,100))
        elif k=='su-helicoid':a=np.linspace(-2,2,70).astype(complex)
        else:a=anciaux(n,1)[0][::5]
        b=anciaux(n,1 if k=='su-helicoid' else -1)[0][::5]
        ia=np.r_[0,np.cumsum((a[1:]-a[:-1])*(np.conj(a[1:])+np.conj(a[:-1]))/2)]
        ib=np.r_[0,np.cumsum((b[1:]-b[:-1])*(np.conj(b[1:])+np.conj(b[:-1]))/2)]
        # Re second coordinate is explicitly retained, so translation is visible.
        def point(i,j):
            prod=a[int(i)]*b[int(j)];integ=ib[int(j)]-ia[int(i)]
            if k=='castro-pair':return [integ.real,prod.real,prod.imag]
            return [prod.real,prod.imag,integ.real]
        mesh(g,point,np.arange(len(a)),np.arange(len(b)));return g
    if k=='lawson-osserman':
        def f(r,Y):u,v=Y;return [v,-(1+v*v)*(v/r+2*(r*v-4*u)/(r*r+4*u*u)+(r*v-u))]
        r0=.002;so=solve_ivp(f,[r0,7],[.025*r0*r0,.05*r0],rtol=1e-10,atol=1e-11,max_step=.01,dense_output=True)
        r=np.linspace(r0,7,250);u=so.sol(r)[0];path(g,np.c_[r,u,np.zeros(len(r))]);line(g,[0,0,0],[7,0,0]);line(g,[0,0,0],[7,u[-1],0],1);return transform(g,lambda v:np.sqrt(2)*v)
    if k=='hyperbolic-bowl':
        def f(s,Y):r,z,a=Y;return [np.cos(a),np.sin(a),2*np.cos(a)-np.sin(a)/np.tanh(r)]
        for neck,col in [(0,0),(.65,1)]:
            if not neck:P=ode(f,[1e-4,0,1e-4],6,110)
            else:P=np.vstack([ode(f,[neck,0,np.pi/2],-5,110)[::-1],ode(f,[neck,0,np.pi/2],5,110)[1:]])
            revolve(g,np.c_[np.tanh(P[:,0]/2),P[:,1]],col)
        return g
    if k=='trumpet-end' and e['id']=='rotational-trumpet-ends':
        def f(x,Y):u,v=Y;return [v,(1+v*v)*(x*v/2-u/2+1/u)]
        x=np.linspace(10,2,180);so=solve_ivp(f,[10,2],[10+1/10,1-1/100],rtol=1e-10,atol=1e-11,max_step=.015,dense_output=True);u=so.sol(x)[0]
        revolve(g,np.c_[u,x]);path(g,[[2,0,2],[10,0,10]],1);return g
    return None

def schematic(e,stage):
    """Explicit orbit/asymptotic diagrams. No sampled PDE claim for these paths."""
    kind=e['visual']['kind'];p=e['visual']['params'];g=geom();v=stage
    a=np.linspace(0,TAU,181);x=np.linspace(-3,3,181)
    if kind=='network':
        typ=p.get('network','');rays=p.get('rays',2)
        if 'cisgeminate' in e['id']:
            # Two four-cells, shared middle edge, four radial exterior rays.
            top=np.c_[1.6*np.cos(a[:91]),.7*np.sin(a[:91])+.18,np.zeros(91)];path(g,top);path(g,top*np.array([1,-1,1]));line(g,[-1.45,0,0],[1.45,0,0],0)
            for s in [-1,1]:
                for q in [-1,1]:line(g,[s*1.45,0,0],[s*1.6,q*.18,0],0);line(g,[s*1.6,q*.18,0],[s*3.3,q*.37125,0],1)
        elif 'spoon' in e['id']:
            t=np.linspace(np.pi/3,5*np.pi/3,180);z=(1+np.cos(t))*np.exp(1j*t);path(g,np.c_[z.real,z.imag]);line(g,[z[-1].real,z[-1].imag,0],[3,0,0],1);line(g,[z[0].real,z[0].imag,0],[3,0,0],0)
        elif 'rocket' in e['id']:
            path(g,[[-1.2,0,0],[-.9,.85,0],[0,1.5,0],[.9,.85,0],[1.2,0,0]]);path(g,[[1.2,0,0],[0,-.8,0],[-1.2,0,0]]);line(g,[-1.2,0,0],[-3,0,0],1);line(g,[1.2,0,0],[3,0,0],1);line(g,[0,1.5,0],[0,3,0],1)
        else:
            path(g,np.c_[1.7*np.cos(a),.85+.7*np.sin(a)*(1+.28*np.cos(a)),np.zeros(len(a))]);line(g,[-1.7,.85,0],[-3,1.5,0],1);line(g,[1.7,.85,0],[3,1.5,0],1)
        return g
    if kind=='drugan-kleene':
        # Four separate meridian boundary-condition diagrams: axis-to-axis,
        # closed, one escaping branch, and two escaping branches.
        t=np.linspace(0,np.pi,130);path(g,np.c_[-2.1+.7*np.cos(t),.9*np.sin(t)*(1+.5*np.cos(2*t)),np.zeros(len(t))])
        t=np.linspace(0,TAU,160);path(g,np.c_[.6*np.cos(t),1+.35*np.sin(t),np.zeros(len(t))],1)
        t=np.linspace(0,1,140);path(g,np.c_[1.5+1.4*t,.9*np.sin(np.pi*t/2)+.25*t,np.zeros(len(t))],2)
        t=np.linspace(-1,1,140);path(g,np.c_[2.1*t,2.8+.35*np.cos(np.pi*t),np.zeros(len(t))],0)
        line(g,[-3,0,0],[3,0,0]);return g
    if kind in ['riedler','cone-topology','periodic-quadric']:
        for j in range(3):
            t=np.linspace(0,TAU,121);r=.55+.12*np.cos((j+2)*t);path(g,np.c_[r*np.cos(t)+2*(j-1),r*np.sin(t)+1,np.zeros(len(t))],j)
        line(g,[-3,0,0],[3,0,0]);
        for j in [-2,0,2]:line(g,[j,.3,0],[j,1.7,0],3)
        return g
    if kind=='ma-fingers':
        t=np.linspace(0,TAU,401);fingers=[5,3,1][v]
        radius=1+.55*np.cos(fingers*t)
        xx=radius*np.cos(t);yy=radius*np.sin(t)
        if v<2:xx+=.65*np.sin((fingers+1)*t)
        path(g,np.c_[xx,yy,np.zeros(len(t))]);return g
    if kind in ['grim-config','space-reapers','immersed-chain']:
        t=np.linspace(-1.43,1.43,91);ends=[]
        for j in range(3 if kind!='ma-fingers' else 5):
            xx=t+(j-1)*1.9;yy=-np.log(np.cos(t))*(1 if j%2==0 else -1)+(.4*j if kind=='grim-config' else (j%2)*2)
            yy+=.35*v*(-1 if j%2 else 1) if kind!='grim-config' else 0
            if kind=='grim-config':mesh(g,lambda i,z:(xx[int(i)],yy[int(i)],z),np.arange(len(t)),np.linspace(-1.5,1.5,9),j%3)
            elif kind=='space-reapers':path(g,np.c_[xx,yy*np.cos(j*np.pi/2),yy*np.sin(j*np.pi/2)],j%3)
            else:path(g,np.c_[xx,yy,np.zeros(len(t))],j%3)
            if kind!='grim-config':
                zz=yy*np.sin(j*np.pi/2) if kind=='space-reapers' else np.zeros(len(t));yyy=yy*np.cos(j*np.pi/2) if kind=='space-reapers' else yy
                ends.append(([xx[0],yyy[0],zz[0]],[xx[-1],yyy[-1],zz[-1]]))
        for i in range(len(ends)-1):line(g,ends[i][1],ends[i+1][0],3)
        if kind=='immersed-chain':path(g,[ends[-1][1],[3.5,-2.5,0],[-3.5,-2.5,0],ends[0][0]],3)
        return g
    if kind in ['polyhedral-translator','polyhedral-pancake','eternal-wedge']:
        sides=3 if kind!='polyhedral-translator' else 4;R=3.8-.7*v if kind!='polyhedral-translator' else 3
        for z in [-.6,.6]:path(g,[[R*np.cos(t),R*np.sin(t),z] for t in np.linspace(0,TAU,sides+1)],0)
        for t in np.linspace(0,TAU,sides,endpoint=False):line(g,[R*np.cos(t),R*np.sin(t),-.6],[R*np.cos(t),R*np.sin(t),.6],1)
        if kind=='eternal-wedge':path(g,[[-4,3,0],[0,.25*v,0],[4,3,0]],2)
        return g
    if kind in ['pancake','anisotropic-oval','ancient-doughnut','perturbed-tori','unstable-boundary']:
        if kind in ['ancient-doughnut','perturbed-tori','unstable-boundary']:
            R=2.3;rr=.65 if kind=='perturbed-tori' else .85-.22*v
            if kind=='unstable-boundary':
                u=brentq(lambda u:u*np.tanh(u)-1,1,1.5);aa=1/np.sqrt(np.cosh(u)**2+u*u)
                revolve(g,[[aa*np.cosh(z/aa),z] for z in np.linspace(-aa*u,aa*u,65)])
                for plane in range(3):path(g,[[np.cos(t),np.sin(t),0] if plane==0 else [np.cos(t),0,np.sin(t)] if plane==1 else [0,np.cos(t),np.sin(t)] for t in a],3)
                for z in [-.25,0,.25]:line(g,[aa*np.cosh(z/aa),0,z],[aa*np.cosh(z/aa)+.08*(v+1),0,z],1)
            else:mesh(g,lambda u,w:((R+rr*np.cos(w))*np.cos(u),(R+rr*np.cos(w))*np.sin(u),rr*np.sin(w)+(.08*v*np.sin(2*u) if kind=='perturbed-tori' else 0)),np.linspace(0,TAU,49),np.linspace(0,TAU,25))
        else:
            A=3.8-.8*v;B=.65 if kind=='pancake' else 2.2-.3*v;C=.8
            mesh(g,lambda u,w:(A*np.cos(u)*np.cos(w),B*np.sin(u)*np.cos(w),C*np.sin(w)),np.linspace(0,TAU,49),np.linspace(-np.pi/2,np.pi/2,25))
            if kind=='pancake':
                for h in [-.85,.85]:path(g,[[-4,-2,h],[4,-2,h],[4,2,h],[-4,2,h],[-4,-2,h]],3)
        return g
    if kind in ['bdg','simons-neck','orbit-neck','cone-unstable','trumpet-end','prescribed-end','gh-neck-pinch']:
        r=np.linspace(.12,4,120);eps=[.8,.35,.08][v]
        if kind=='bdg':mesh(g,lambda x,y:(x,y,.18*(x*x-y*y)),np.linspace(-3,3,29),np.linspace(-3,3,29))
        elif kind in ['simons-neck','orbit-neck','cone-unstable','trumpet-end']:
            line(g,[0,0,0],[4,4,0],3);path(g,np.c_[r,np.sqrt(r*r+eps*eps),np.zeros(len(r))]);path(g,np.c_[np.sqrt(r*r+eps*eps),r,np.zeros(len(r))],1)
            circle(g,eps,center=(0,0),color=2)
        elif kind=='prescribed-end':
            for j in range(4):path(g,[[np.sqrt(j+1)*(1+.22*np.cos(3*t))*np.cos(t),np.sqrt(j+1)*(1+.22*np.cos(3*t))*np.sin(t),j*1.5] for t in a],j%3)
            circle(g,.6,color=3)
        else:
            xx=np.linspace(-3,3,150);yy=.7*np.exp(-xx*xx)*(1-v/2);path(g,np.c_[xx,yy,np.zeros(len(xx))]);
            for c in [-3,0,3]:circle(g,.07,(c,0),1)
            for j in [-1.5,-.5,0,.5,1.5]:
                rr=.17*(1-v/2) if j==0 else .17
                path(g,[[j,.7*np.exp(-j*j)*(1-v/2)+rr*np.cos(t),rr*np.sin(t)] for t in a[::3]],2)
        return g
    if kind in ['free-boundary','free-boundary-domain','mixed-boundary']:
        circle(g,1)
        if kind=='free-boundary':
            c=[8,2.2,1.15][v];rr=np.sqrt(c*c-1);theta=np.arccos(rr/c)
            tt=np.linspace(np.pi-theta,np.pi+theta,121);path(g,np.c_[c+rr*np.cos(tt),rr*np.sin(tt),np.zeros(len(tt))])
        elif kind=='free-boundary-domain':
            g=transform(g,lambda a:a*np.array([1.5,1,1]));t=np.linspace(-1,1,121);path(g,np.c_[1.5*t,.18*v*(1-t*t),np.zeros(len(t))]);line(g,[-1.5,0,0],[1.5,0,0],3)
        else:
            tt=np.linspace(0,1,121);angle=[.15,1.1,2.8][v];end=np.array([np.cos(angle),np.sin(angle)]);start=np.array([-.5,0]);control=end-.7*end
            curve=(1-tt[:,None])**2*start+2*(1-tt[:,None])*tt[:,None]*control+tt[:,None]**2*end;path(g,curve);circle(g,.035,(-.5,0),1)
        return g
    if kind=='tetrahedral-junction':
        pts=np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]])/np.sqrt(3)
        for i in range(4):line(g,[0,0,0],pts[i]*3,i%3)
        for i in range(4):
            for j in range(i):path(g,[pts[i]*2,[0,0,.12*v],pts[j]*2],(i+j)%3)
        return g
    if kind=='hyperbolic-parabolic':
        xx=np.linspace(-2.8,2.8,161);zz=.35+.4/np.cosh(xx)
        mesh(g,lambda i,y:(xx[int(i)],y,zz[int(i)]),np.arange(len(xx)),np.linspace(-1,1,11))
        path(g,[[-3,-1.5,0],[3,-1.5,0],[3,1.5,0],[-3,1.5,0],[-3,-1.5,0]],3);return g
    if kind in ['hyperbolic-grims','hyperbolic-curves']:
        xx=np.linspace(-2.8,2.8,181);yy=.35+.4/np.cosh(xx);path(g,np.c_[xx,yy,np.zeros(len(xx))]);line(g,[-4,0,0],[4,0,0],3)
        if kind!='hyperbolic-curves':mesh(g,lambda i,z:(xx[int(i)],yy[int(i)],z),np.arange(len(xx)),np.linspace(-1,1,9))
        return g
    if kind in ['hyperbolic-helicoid','nil-translator','sol-translator','sl2-translator','compact-product','hyperbolic-catenoid']:
        if kind=='hyperbolic-helicoid':
            t=np.linspace(-4,4,160);r=.12+.12*np.abs(t);ph=.8*t;mesh(g,lambda i,w:(r[int(i)]*np.cos(ph[int(i)]+w),r[int(i)]*np.sin(ph[int(i)]+w),.3*w),np.arange(len(t)),np.linspace(-3,3,25))
        elif kind=='hyperbolic-catenoid':
            t=np.linspace(-2,2,100);revolve(g,np.c_[1+.5*t*t,1.5+.5*t+.3*t*t]);line(g,[-3,0,0],[3,0,0],3)
        elif kind=='nil-translator':revolve(g,[[r,.3*r*r] for r in np.linspace(0,3,60)])
        elif kind=='sol-translator':mesh(g,lambda u,w:(u,w,.4*np.log(1+w*w)),np.linspace(-2,2,15),np.linspace(-2,2,45))
        elif kind=='sl2-translator':
            path(g,[[s,1+.2*s*s,0] for s in x]);
            for s in [-2,0,2]:path(g,[[s+.3*np.cos(t),1+.2*s*s,.3*np.sin(t)] for t in a],1)
        else:
            t=np.linspace(-1.35,1.35,151);path(g,np.c_[t,-np.log(np.cos(t)),np.zeros(len(t))]);line(g,[-1.57,0,0],[1.57,0,0],3)
        return g
    raise ValueError('No intentional geometry for '+kind)


def exact_product(kind,t):
    if kind=='euclidean-product':a,b=np.sqrt(2-2*t),np.sqrt(5-2*t)
    else:a,b=np.sqrt(.5+.4*np.exp(4*t)),np.sqrt(.5-.4*np.exp(4*t))
    g=geom();mesh(g,lambda u,v:(a*np.cos(u),a*np.sin(u)+.35*b*np.sin(v),b*np.cos(v)),np.linspace(0,TAU,49),np.linspace(0,TAU,33));return g

def frames_for(e):
    k=e['visual']['kind'];motion=e['visual']['motion']
    if k=='graph-expander':return graph_flow(),['t = 0.25','t = 1','t = 2.25'],'physical-time'
    if k=='hyperbolic-curves':
        base=schematic(e,0)
        return [transform(base,lambda v,t=t:v+np.array([t,0,0])) for t in [-1,0,1]],['group time −1','group time 0','group time 1'],'isometry'
    if k=='sine-wave':
        out=[]
        for t in [-2,0,2]:g=geom();x=np.linspace(-2*np.pi,2*np.pi,501);path(g,np.c_[x,np.arcsinh(np.exp(-t)*np.sin(x)),np.zeros(len(x))]);out.append(g)
        return out,['t = −2','t = 0','t = 2'],'physical-time'
    if k in ['euclidean-product','sphere-product']:
        times=[-2,-.5,.8] if k=='euclidean-product' else [-1,-.3,0]
        return [exact_product(k,t) for t in times],['t = '+str(t) for t in times],'physical-time'
    base=base_numeric(e)
    if base is None:base=schematic(e,0)
    if e['category'] in ['shrinkers','expanders'] and k!='tetrahedral-junction':
        scales=[2,1,.5] if e['category']=='shrinkers' else [.5,1,2];times=[-4,-1,-.25] if e['category']=='shrinkers' else [.25,1,4]
        return [transform(base,lambda v,s=s:v*s) for s in scales],['t = '+str(t) for t in times],'homothety'
    if e['category']=='translators':
        frames=[]
        for t in [-1,0,1]:
            if k=='hyperbolic-catenoid':fn=lambda v,t=t:v*np.exp(.35*t)
            elif k=='sol-translator':fn=lambda v,t=t:np.array([v[0]*np.exp(-.35*t),v[1]*np.exp(.35*t),v[2]+.35*t])
            elif k=='hyperbolic-parabolic':fn=lambda v,t=t:v+np.array([t,0,0])
            elif k in ['grim-config','compact-product']:fn=lambda v,t=t:v+np.array([0,t,0])
            elif k=='sl2-translator':fn=lambda v,t=t:v+np.array([t,0,0])
            elif k=='castro-pair':fn=lambda v,t=t:v+np.array([t,0,0])
            else:fn=lambda v,t=t:v+np.array([0,0,t*(2 if k=='hyperbolic-bowl' else 1)])
            frames.append(transform(base,fn))
        labels=['τ = −0.35','τ = 0','τ = 0.35'] if k in ['hyperbolic-catenoid','sol-translator'] else ['t = −1','t = 0','t = 1'] if k in ['hyperbolic-bowl','castro-pair','su-pair','su-helicoid'] else ['group time −1','group time 0','group time 1']
        return frames,labels,'isometry'
    return [schematic(e,v) for v in range(3)],['earlier stage','intermediate stage','later stage'],'schematic-stages'


def projection(v):x,y,z=v;return [x*.86-y*.5,(x*.5+y*.86)*.32-z*.95]
def static_svg(data):
    frames=data.get('variants',[{'frames':data['frames']}])[0]['frames'];flat_mode=all(abs(v[2])<1e-9 for g in frames for v in g['vertices']);project=(lambda v:[v[0],-v[1]]) if flat_mode else projection;flat=[project(v) for g in frames for v in g['vertices']];A=np.array(flat);center=(A.min(0)+A.max(0))/2;span=max(np.ptp(A,axis=0));scale=185/max(span,1e-9)
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" role="img" aria-labelledby="title desc"><title id="title">'+html.escape(data['title'])+'</title><desc id="desc">'+html.escape(data['caption'])+'</desc><rect width="900" height="390" fill="#f8faf9"/>']
    out.append('<text x="24" y="28" font-family="sans-serif" font-size="15" fill="#184047">'+html.escape(data['displayStatus'])+'</text>')
    for j,g in enumerate(frames):
        def point(v):q=(np.array(project(v))-center)*scale;return f'{150+j*300+q[0]:.2f},{190+q[1]:.2f}'
        out.append(f'<text x="{150+j*300}" y="61" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#344c50">{html.escape(data["timeLabels"][j])}</text>')
        for face,col in zip(g['faces'],g['faceColors']):out.append('<polygon points="'+' '.join(point(g['vertices'][i]) for i in face)+'" fill="'+COLORS[col%4]+'" fill-opacity=".11" stroke="'+COLORS[col%4]+'" stroke-opacity=".12" stroke-width=".45"/>')
        for p,col in zip(g['paths'],g['pathColors']):out.append('<polyline points="'+' '.join(point(g['vertices'][i]) for i in p)+'" fill="none" stroke="'+COLORS[col%4]+'" stroke-width="1.5"/>')
    out.append('<text x="450" y="360" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#52656b">Common spatial scale · teal: profile / slice · rust: second piece / asymptote · gray: reference geometry</text></svg>')
    return ''.join(out)

def selected_geometry(g,face_pred,path_pred):
    faces=[f for i,f in enumerate(g['faces']) if face_pred(i,g['faceColors'][i])]
    paths=[p for i,p in enumerate(g['paths']) if path_pred(i,g['pathColors'][i])]
    fc=[c for i,c in enumerate(g['faceColors']) if face_pred(i,c)];pc=[c for i,c in enumerate(g['pathColors']) if path_pred(i,c)]
    used=sorted(set(i for p in faces+paths for i in p));remap={old:new for new,old in enumerate(used)}
    return dict(vertices=[g['vertices'][i] for i in used],faces=[[remap[i] for i in f] for f in faces],paths=[[remap[i] for i in p] for p in paths],faceColors=fc,pathColors=pc)

def main():
    manifest=json.loads((ROOT/'documentation/literature-additions.json').read_text());OUT.mkdir(exist_ok=True)
    for e in manifest['entries']:
        frames,labels,mode=frames_for(e);first=frames[1]
        # Round storage only after integration and diagnostics.
        for g in frames:g['vertices']=np.round(g['vertices'],7).tolist()
        data=dict(kind='literature-flow',title=e['title'].replace('--','–'),caption=e['visual']['caption'],displayStatus=e['visual']['status'],status='numerical-ode' if e['visual']['status'].startswith('Numerical ODE') else 'illustration',frames=frames,timeLabels=labels,timeMode=mode,vertices=first['vertices'],faces=first['faces'],paths=first['paths'],sourceKeys=e['citations'],family=e['id'],geometryKind=e['visual']['kind'])
        if e['visual']['kind']=='hyperbolic-bowl':
            data['variants']=[dict(label=label,frames=[selected_geometry(g,lambda i,c,col=col:c==col,lambda i,c,col=col:c==col) for g in frames]) for col,label in [(0,'Rotational bowl'),(1,'Translating catenoid')]]
        if e['visual']['kind']=='birotational':
            data['variants']=[dict(label='Orbit-space meridian',frames=[selected_geometry(g,lambda i,c:False,lambda i,c:i<3) for g in frames]),dict(label='Projected sphere-pair orbits',frames=[selected_geometry(g,lambda i,c:True,lambda i,c:i>=3) for g in frames])]
        if e['visual']['kind']=='anciaux':
            data['variants']=[dict(label='Complex profile γ',frames=[selected_geometry(g,lambda i,c:False,lambda i,c:c==1) for g in frames]),dict(label='Projected two-dimensional slice',frames=[selected_geometry(g,lambda i,c:True,lambda i,c:c==0) for g in frames])]
        if e['visual']['kind']=='hyperbolic-grims':
            base=schematic(e,0);data['variants']=[]
            for variant in ['Vertical','Parabolic','Hyperbolic']:
                fs=[]
                for t in [-1,0,1]:
                    fn=(lambda v,t=t:v+np.array([0,0,t])) if variant=='Vertical' else (lambda v,t=t:v+np.array([t,0,0])) if variant=='Parabolic' else (lambda v,t=t:v*np.array([np.exp(t),np.exp(t),1]))
                    fs.append(transform(base,fn))
                data['variants'].append(dict(label=variant+' Killing motion',frames=fs))
        dest=OUT/('literature-'+e['id']);dest.with_suffix('.json').write_text(json.dumps(data,separators=(',',':'),default=lambda x:int(x))+'\n');dest.with_suffix('.svg').write_text(static_svg(data))
        print(e['id'],len(first['vertices']))
    (ROOT/'documentation/literature-figure-diagnostics.json').write_text(json.dumps(AUDIT,indent=2)+'\n')
if __name__=='__main__':main()
