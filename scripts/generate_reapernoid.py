#!/usr/bin/env python3
"""Numerical finite-start reapernoid approximations, Mramor--Payne (2019), (2.7).

These truncated-domain computations do not construct or certify an eternal limit.
Requires NumPy/SciPy only for regeneration; the reader uses the saved data.
"""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from scipy.special import beta
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/solitons'

def solve(n=2,delta=1e-4,N=600,L=None,T=100,rtol=2e-8):
    m=n-1
    half=float('inf') if n==2 else float(beta((n-2)/(2*m),.5)/(2*m))
    if L is None:L=7.0 if n==2 else half-.005
    x=np.linspace(0,L,N+1);h=x[1]
    if n==2:
        base=lambda z:(np.cosh(z),np.sinh(z))
    else:
        ode=solve_ivp(lambda z,y:[y[1],m*(1+y[1]**2)/y[0]],(0,L+1.3*delta),[1.,0.],dense_output=True,rtol=2e-12,atol=1e-13)
        assert ode.success
        base=lambda z:ode.sol(z)
    w,p=base(x);wpp=m*(1+p*p)/w
    # A true outward parallel offset, re-expressed as a graph over the axis.
    s=x.copy()
    for _ in range(16):
        r,q=base(s);s=x+delta*q/np.sqrt(1+q*q)
    r,q=base(s);initial=r+delta/np.sqrt(1+q*q)-w;fixed=float(initial[-1])
    def rhs(t,v):
        full=np.r_[v,fixed]
        vx=np.r_[0,(full[2:]-full[:-2])/(2*h)]
        vxx=np.r_[2*(full[1]-full[0])/h**2,(full[2:]-2*full[1:-1]+full[:-2])/h**2]
        u=w[:-1]+v
        # Algebraic form of (w''+v'')/(1+(w'+v')²)-m/(w+v).
        # The stationary catenoid is represented exactly, avoiding startup drift.
        return (wpp[:-1]*v+u*vxx-m*(2*p[:-1]*vx+vx*vx))/((1+(p[:-1]+vx)**2)*u)
    def hit(t,v):return v[0]-1
    hit.terminal=True;hit.direction=1
    sparsity=diags([np.ones(N-1),np.ones(N),np.ones(N-1)],[-1,0,1],format='csc')
    kwargs=dict(method='BDF',rtol=rtol,atol=rtol/100,jac_sparsity=sparsity,dense_output=True,max_step=.2)
    old=solve_ivp(rhs,[0,50],initial[:-1],events=hit,**kwargs)
    assert old.success and len(old.t_events[0])==1
    shift=float(old.t_events[0][0])
    future=solve_ivp(rhs,[0,T],old.y[:,-1],**kwargs)
    assert future.success
    def sample(t,points):
        v=old.sol(shift+t) if t<0 else future.sol(t)
        # Interpolate the smooth perturbation, adding the analytic/ODE base at x.
        points=np.asarray(points)
        return np.asarray(base(abs(points))[0])+np.interp(abs(points),x,np.r_[v,fixed])
    def metrics(t):
        v=old.sol(shift+t) if t<0 else future.sol(t);u=w[:-1]+v;f=rhs(0,v)
        full=np.r_[v,fixed]
        vx=np.r_[0,(full[2:]-full[:-2])/(2*h)]
        vxx=np.r_[2*(full[1]-full[0])/h**2,(full[2:]-2*full[1:-1]+full[:-2])/h**2]
        curvature=(wpp[:-1]+vxx)/(1+(p[:-1]+vx)**2)**1.5
        interior=x[:-1]<(2.2 if n==2 else 1.1)
        dt=1e-3
        if t>-.5*shift and t<T-dt:
            a=old.sol(shift+t-dt) if t-dt<0 else future.sol(t-dt)
            b=old.sol(shift+t+dt) if t+dt<0 else future.sol(t+dt)
            residual=float(np.max(abs((b-a)/(2*dt)-f)[interior]))
        else:residual=None
        return dict(time=t,neck_radius=float(u[0]),neck_speed=float(f[0]),meridian_tip_curvature=float(curvature[0]),
                    minimum_outward_speed=float(f[interior].min()),minimum_meridian_curvature=float(curvature[interior].min()),
                    minimum_gap_above_catenoid=float(v[interior].min()),temporal_residual_in_display_window=residual)
    return dict(n=n,x=x,half=half,delta=delta,grid=N,domain=L,shift=shift,sample=sample,metrics=metrics,base=base)

def compare(a,b,times,window):
    points=np.linspace(-window,window,141)
    return [dict(time=t,max_profile_difference=float(np.max(abs(a['sample'](t,points)-b['sample'](t,points))))) for t in times]

def make_case(n):
    N=600 if n==2 else 700;T=100 if n==2 else 40
    a=solve(n,N=N,T=T)
    times=np.unique(np.r_[np.linspace(-10 if n==2 else -3,0,41),np.linspace(0,np.sqrt(T),81)**2,
                         [-8,-4,0,10,40,100] if n==2 else [-2,-1,0,5,15,40]])
    times=np.unique(np.round(times,8))
    points=np.linspace(-2.2,2.2,221) if n==2 else np.linspace(-1.17,1.17,235)
    frames=[dict(t=round(float(t),8),u=np.round(a['sample'](t,points),8).tolist(),**{k:v for k,v in a['metrics'](float(t)).items() if k in ['neck_radius','neck_speed','meridian_tip_curvature']}) for t in times]
    checkpoints=[-8,-4,0,10,40,100] if n==2 else [-2,-1,0,5,15,40]
    audit=dict(n=n,ambient_dimension=n+1,delta=a['delta'],grid_intervals=N,half_domain=a['domain'],start_time=-a['shift'],
               time_origin='First time the neck radius reaches 2; the limiting catenoid has neck radius 1.',
               boundary='Even reflection at x=0; fixed initial radius at the artificial outer boundary.',
               checkpoints=[a['metrics'](t) for t in checkpoints])
    # Independent changes to space resolution, normal offset, time tolerance and end cutoff.
    fine=solve(n,N=2*N,T=T)
    smaller=solve(n,N=N,delta=1e-5,T=T)
    longer=solve(n,N=N+200,L=8.0 if n==2 else a['half']-.0025,T=T)
    tighter=solve(n,N=N,T=T,rtol=2e-9)
    for key,other in [('mesh_refinement',fine),('smaller_initial_offset',smaller),('longer_domain',longer),('tighter_time_tolerance',tighter)]:
        audit[key]=compare(a,other,checkpoints,2 if n==2 else 1)
    case=dict(n=n,ambient=n+1,x=np.round(points,8).tolist(),reference=np.round(a['base'](abs(points))[0],8).tolist(),frames=frames,half_width=None if n==2 else a['half'],
              time=dict(min=-8 if n==2 else -2,max=T,value=0),surface_time=dict(min=-8,max=10,value=0) if n==2 else None,
              snapshots=[-8,-4,0,10] if n==2 else [-2,0,15,40],profile_snapshots=[-8,0,40,100] if n==2 else [-2,0,15,40],
              delta=a['delta'],simulation_start=-a['shift'],computational_half_domain=a['domain'])
    print('Case',n,'checks:',json.dumps({key:max(x['max_profile_difference'] for x in audit[key]) for key in ['mesh_refinement','smaller_initial_offset','longer_domain','tighter_time_tolerance']}),flush=True)
    return case,audit

def main():
    pairs=[make_case(n) for n in [2,3]]
    data=dict(kind='reapernoid-pde',name='The eternal reapernoid: numerical approximations',status='numerical-pde',
              cases=[p[0] for p in pairs],view=dict(yaw=.58,pitch=.40),
              source='Mramor–Payne, arXiv:1904.08439v2, (2.7), Theorem 1.3, and §4.',
              description='Finite-start, truncated-domain numerical solutions of the rotational MCF equation. Time is shifted so u(0,0)=2. These approximate the construction; convergence to an eternal flow is not certified.',
              vertices=[[0,0,0]],faces=[],paths=[])
    # A genuine default annular mesh also supports the common geometry validator.
    c=data['cases'][0];frame=next(f for f in c['frames'] if f['t']==0)
    xs=np.linspace(-2,2,61);rs=np.interp(xs,c['x'],frame['u']);segments=40
    data['mesh_x']=xs.tolist();data['segments']=segments
    data['vertices']=[[float(r*np.cos(2*np.pi*j/segments)),float(r*np.sin(2*np.pi*j/segments)),float(x)] for x,r in zip(xs,rs) for j in range(segments)]
    data['faces']=[]
    for i in range(len(xs)-1):
        for j in range(segments):
            a=i*segments+j;b=i*segments+(j+1)%segments;c=a+segments;d=b+segments
            data['faces'].extend([[a,c,d],[a,d,b]])
    data['paths']=[[i*segments+j for j in range(segments)]+[i*segments] for i in [0,len(xs)-1]]
    (OUT/'reapernoid.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'reapernoid-audit.json').write_text(json.dumps(dict(cases=[p[1] for p in pairs]),indent=2)+'\n')
if __name__=='__main__':main()
