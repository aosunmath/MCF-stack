"""Original ODE/formula figures after Halldorsson (2012, 2013); not certified numerics.
Run with NumPy/SciPy. Source equations and finite windows accompany each data set.
"""
from pathlib import Path
from html import escape
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/solitons'
AUDIT={}

def solve(fun, y0, end, tol=2e-10):
    sol=solve_ivp(fun,(0,end),y0,method='DOP853',rtol=tol,atol=tol/20,dense_output=True,max_step=.06)
    if not sol.success: raise ValueError(sol.message)
    return sol

def planar(A,B,y0,L=40,n=2201):
    fun=lambda s,y:[y[0]*y[1]+A,-y[0]**2-B,y[0]]
    s=np.linspace(-L,L,n)
    back=solve(fun,y0,-L); forward=solve(fun,y0,L)
    y=np.where(s[None,:]<0,back.sol(s),forward.sol(s))
    z=np.exp(1j*y[2])*(y[0]+1j*y[1])/(A-1j*B)
    check=solve(fun,y0,L,tol=1e-11).sol(s[s>=0])
    zc=np.exp(1j*check[2])*(check[0]+1j*check[1])/(A-1j*B)
    error=float(np.max(abs(zc-z[s>=0])))
    # Independent central differences of the reconstructed immersion.
    ds=s[1]-s[0]; dz=(z[2:]-z[:-2])/(2*ds)
    tangent_error=float(np.max(abs(dz-np.exp(1j*y[2,1:-1]))))
    return dict(vertices=np.column_stack([z.real,z.imag,np.zeros(len(z))]).round(8).tolist(),
                paths=[list(range(n))],faces=[],A=A,B=B,window=[-L,L],
                diagnostics=dict(refinement_max=error,unit_tangent_difference=tangent_error))

def dense_profile():
    # Curvature period from the upward return to v=0 (start at minimum radius).
    def period(r):
        def rhs(s,y): return [y[0]*y[1],.5-y[0]**2,y[0]]
        eps=1e-7; y0=[r/2,eps*(.5-r*r/4),eps*r/2]
        def event(s,y): return y[1]
        event.direction=1;event.terminal=True
        sol=solve_ivp(rhs,(eps,30),y0,method='DOP853',rtol=2e-12,atol=1e-13,events=event,max_step=.025)
        if len(sol.t_events[0])!=1: raise ValueError('No phase return')
        return sol.t_events[0][0],sol.y_events[0][0][2]/(2*np.pi)
    target=(np.sqrt(5)-1)/2
    r=brentq(lambda r:period(r)[1]-target,.03,1.3,xtol=1e-12)
    P,alpha=period(r)
    v=planar(0,-.5,[r/2,0,0],L=5*P,n=4001)
    v.update(name='Irrational turning target',note='Ten curvature periods; target α=(√5−1)/2. Irrationality is imposed mathematically, not certified numerically.')
    AUDIT['dense_shooting']=dict(target=float(target),r_min=float(r),period=float(P),turning_residual=float(alpha-target))
    return v

def mesh(z,heights,angles):
    vertices=[[float((np.exp(1j*p)*v).real),float((np.exp(1j*p)*v).imag),float(h)] for v in z for p,h in zip(angles,heights)]
    m=len(angles); faces=[]
    for i in range(len(z)-1):
        for j in range(m-1):
            a=i*m+j;faces.extend([[a,a+m,a+m+1],[a,a+m+1,a+1]])
    paths=[list(range(i*m,(i+1)*m)) for i in range(0,len(z),20)]
    paths += [list(range(j,len(vertices),m)) for j in [0,m//2,m-1]]
    return dict(vertices=np.round(vertices,8).tolist(),faces=faces,paths=paths)

def helicoidal(h,d):
    def rhs(s,y):
        tau,nu,theta=y;k=(tau*(tau*tau+h*h)-nu)/(tau*tau+nu*nu+h*h)
        return [1+k*nu,-k*tau,k]
    s=np.linspace(-18,18,321);y0=[0,d,0]
    b=solve(rhs,y0,-18);f=solve(rhs,y0,18)
    y=np.where(s[None,:]<0,b.sol(s),f.sol(s))
    z=(y[0]+1j*y[1])*np.exp(1j*y[2]); phi=np.linspace(-np.pi,np.pi,37)
    v=mesh(z,h*phi,phi)
    tau,nu=y[:2];k=(tau*(tau*tau+h*h)-nu)/(tau*tau+nu*nu+h*h)
    H=-h*(k*(tau*tau+nu*nu+h*h)+nu)/(tau*tau+h*h)**1.5
    residual=float(np.max(abs(H+h*tau/np.sqrt(tau*tau+h*h))))
    AUDIT[f'helicoidal_h{h}_d{d}']=dict(mean_curvature_translator_residual=residual,arclength_window=[-18,18],screw_angle=[-float(np.pi),float(np.pi)])
    return dict(**v,name=f'Pitch h={h}, minimum radius d={d}',h=h,note='Numerical helicoidal translator; finite patch. The complete surface has no boundary. Translation speed is h downward.',window=[-18,18])

def minimal(h,a):
    u=np.linspace(-2.4/h,2.4/h,161);phi=np.linspace(-np.pi,np.pi,45)
    z=(h*np.sinh(h*u)+1j*a*np.cosh(h*u))*np.exp(-1j*a*u)
    return dict(**mesh(z,h*phi,phi),h=h,a=a,name=f'Pitch h={h}, a={a}',note='Exact minimal immersion sampled on a finite patch; stationary for all time.',window=[float(u[0]),float(u[-1])])

def svg(name,data):
    v=data['variants'][0];p=np.array(v['vertices']);p=p-(p.max(axis=0)+p.min(axis=0))/2
    if data['dimension']==3:
        yaw=.55;pitch=.38
        q=np.column_stack([p[:,0]*np.cos(yaw)-p[:,1]*np.sin(yaw),p[:,2]*np.cos(pitch)-(p[:,0]*np.sin(yaw)+p[:,1]*np.cos(yaw))*np.sin(pitch),(p[:,0]*np.sin(yaw)+p[:,1]*np.cos(yaw))*np.cos(pitch)+p[:,2]*np.sin(pitch)])
    else:q=p
    scale=min(550/max(np.ptp(q[:,0]),.1),300/max(np.ptp(q[:,1]),.1));xy=np.column_stack([320+q[:,0]*scale,190-q[:,1]*scale])
    out=[]
    if data['dimension']==3:
        for face in sorted(v['faces'],key=lambda f:float(np.mean(q[f,2]))):
            pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in xy[face]);out.append(f'<polygon points="{pts}" fill="#83b4c2" stroke="#35738b" stroke-width=".22"/>')
    for path in v['paths']:
        pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in xy[path]);out.append(f'<polyline points="{pts}" fill="none" stroke="#195871" stroke-width="1.8"/>')
    if v.get('circle'):
        out.append(f'<circle cx="320" cy="190" r="{v["circle"]*scale:.2f}" fill="none" stroke="#c16f36" stroke-dasharray="5 5"/>')
    label='Exact formula · finite patch' if data['motion']=='stationary' else 'Numerical ODE · finite window'
    (OUT/f'{name}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 410" role="img"><title>'+escape(data['title'])+'</title><rect width="640" height="410" fill="#f7fafb"/>'+''.join(out)+f'<text x="320" y="378" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#355862">{label}</text></svg>\n')

def save(name,title,dimension,motion,variants):
    data=dict(title=title,dimension=dimension,motion=motion,variants=variants)
    (OUT/f'{name}.json').write_text(json.dumps(data,separators=(',',':'))+'\n');svg(name,data)
    html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="../assets/halldorsson-viewer.css"><main data-model="{name}"><h1>{title}</h1><p class="notice">{'Exact formula' if motion=='stationary' else 'Numerical ODE approximation'} · finite display window</p><div class="controls"><label>Profile <select id="profile"></select></label><label><span id="time-label">Time</span> <input id="time" type="range" min="-2" max="2" step="0.01" value="0"></label><output id="time-value"></output><button id="play" type="button">Play</button><label>Zoom <input id="zoom" type="range" min="0.5" max="3" step="0.05" value="1"></label><button id="reset" type="button">Reset view</button></div><canvas width="900" height="550" tabindex="0" role="img" aria-label="{title}; use arrow keys to rotate the three-dimensional view"></canvas><p id="note"></p><p id="help">{'Drag to rotate; arrow keys also rotate.' if dimension==3 else 'All coordinates are in the plane; equal scale on both axes.'} The viewing boundary is not a boundary of the complete solution.</p><p id="error" role="status"></p><p><a href="../numerical-references/">Sources and numerical methods</a></p></main><script type="application/json" id="geometry">{json.dumps(data,separators=(",",":"))}</script><script type="module">{(ROOT/'site/assets/halldorsson-viewer.mjs').read_text()}</script></html>'''
    (ROOT/'site/experiments').mkdir(exist_ok=True)
    (ROOT/f'site/experiments/{name}.html').write_text(html+'\n')
    for i,v in enumerate(variants):
        if 'diagnostics' in v:AUDIT[f'{name}_{i}']=v['diagnostics']


def main():
    # Keep the dense-curve's richer time-comparison viewer when regenerating all figures.
    from generate_annulus_shrinker import generate
    generate()
    dense_profile()  # Retain the original golden-ratio shooting audit.
    variants=[]
    for d in [0,1,2]:
        v=planar(1,0,[0,d,0],L=75);v.update(name=f'Minimum radius d={d}',note='Pure rotation with A=1. Both arms continue to infinity.');variants.append(v)
    save('halldorsson-rotators','Rotating planar curves',2,'similarity',variants)
    variants=[]
    for B,d in [(.25,0),(.25,2),(.5,0)]:
        v=planar(1,B,[B*d,d,0],L=50);v.update(name=f'A=1, B={B}, d={d}',note='Rotating expansion. The logarithmic time control applies the exact similarity motion.');variants.append(v)
    save('halldorsson-expanding','Rotating and expanding spirals',2,'similarity',variants)
    variants=[]
    for B,y in [(-.25,0),(-.25,3),(-1,0)]:
        v=planar(1,B,[0,y,0],L=36,n=3001);v.update(name=f'Bounded profile: A=1, B={B}, v₀={y}',circle=1/np.sqrt(-B),note='Both intrinsic ends accumulate on the dashed circle. It is an asymptotic set, not an extra component.');variants.append(v)
    # Forward shooting from a large-radius asymptotic condition approximates a comet.
    # This does not prove convergence to the complete special trajectory or uniqueness.
    B=-.25; y=-20.;A=1;u=-A/y-A*B/y**3
    rhs=lambda s,z:[z[0]*z[1]+A,-z[0]**2-B,z[0]]
    s=np.linspace(0,160,5001);sol=solve(rhs,[u,y,0],160);v=sol.sol(s);z=np.exp(1j*v[2])*(v[0]+1j*v[1])/(A-1j*B)
    variants.append(dict(name='Comet: asymptotic shooting approximation',vertices=np.column_stack([z.real,z.imag,np.zeros(len(z))]).round(8).tolist(),paths=[list(range(len(z)))],faces=[],A=A,B=B,circle=2,window=[0,160],note='Comet illustration from finite-radius asymptotic initial data v₀=−20. This is an approximate shooting orbit, not a certified complete comet or uniqueness proof.'))
    save('halldorsson-shrinking','Rotating shrinking curves and comets',2,'similarity',variants)
    save('halldorsson-helicoidal','Helicoidal rotating translators',3,'translator',[helicoidal(h,d) for h,d in [(1,0),(1,1),(2,0),(.5,1)]])
    save('halldorsson-minimal','Helicoidal minimal surfaces',3,'stationary',[minimal(h,a) for h,a in [(1,0),(1,1),(.5,1)]])
    (OUT/'halldorsson-audit.json').write_text(json.dumps(dict(method='SciPy DOP853; tolerances 2e-10 and 1e-11, max step 0.06. Dense turning shoot uses 2e-12.',limitations='Floating-point diagnostics; no rigorous error bounds. Finite windows do not prove global topology, irrationality, or completeness.',checks=AUDIT),indent=2)+'\n')

if __name__=='__main__':main()
