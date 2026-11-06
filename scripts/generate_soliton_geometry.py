"""Regenerate original illustrative geometry (requires NumPy and SciPy).

Formula meshes are sampled exactly; ODE meshes are numerical illustrations,
not computer-assisted existence proofs. Source equations are documented in
site/assets/solitons/geometry-audit.json and the catalogue entries.
"""
from pathlib import Path
import json
import math
from html import escape
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
OUT.mkdir(parents=True, exist_ok=True)
AUDIT = {}


def surface(name, f, us, vs, **meta):
    vertices = [list(f(float(u), float(v))) for u in us for v in vs]
    m, n = len(us), len(vs)
    faces = []
    for i in range(m-1):
        for j in range(n-1):
            a=i*n+j
            faces += [[a,a+n,a+n+1],[a,a+n+1,a+1]]
    return save(name, vertices, faces=faces, **meta)


def revolution(name, profile, **meta):
    theta = np.linspace(0, 2*np.pi, 49)
    return surface(name, lambda i,t:(profile[int(i)][1]*math.cos(t),profile[int(i)][1]*math.sin(t),profile[int(i)][0]), range(len(profile)), theta, **meta)


def save(name, vertices, faces=None, paths=None, **meta):
    data = {'name':name, 'vertices':np.round(vertices,7).tolist(), 'faces':faces or [], 'paths':paths or [], **meta}
    (OUT / (name+'.json')).write_text(json.dumps(data, separators=(',',':'))+'\n')
    svg(name,data)
    return data


def svg(name, data):
    p=np.array(data['vertices'], dtype=float)
    if p.shape[1]>3:
        angle=.55
        p[:,1]=np.cos(angle)*p[:,1]-np.sin(angle)*p[:,3]
        p=p[:,:3]
    p=p-(p.max(axis=0)+p.min(axis=0))/2
    if data.get('flat'):
        q=p
    else:
        yaw,pitch=.64,data.get('view',{}).get('pitch',.43)
        horizontal=p[:,0]*np.cos(yaw)-p[:,1]*np.sin(yaw)
        depth=p[:,0]*np.sin(yaw)+p[:,1]*np.cos(yaw)
        q=np.column_stack([horizontal,p[:,2]*np.cos(pitch)-depth*np.sin(pitch),p[:,2]*np.sin(pitch)+depth*np.cos(pitch)])
    span=np.ptp(q[:,:2],axis=0)
    scale=min(560/max(span[0],1e-6),330/max(span[1],1e-6))
    xy=np.column_stack([320+scale*q[:,0],205-scale*q[:,1]])
    items=[]
    for face in sorted(data['faces'],key=lambda f:float(np.mean(q[f,2]))):
        a,b,c=q[face]
        normal=np.cross(b-a,c-a)
        norm=np.linalg.norm(normal)
        light=.45+.5*abs(float(normal@np.array([.3,.5,.8]))/(norm or 1))
        rgb=tuple(int(base*light+255*(1-light)*.25) for base in (67,139,169))
        pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in xy[face])
        items.append(f'<polygon points="{pts}" fill="rgb{rgb}" stroke="#24566b" stroke-opacity=".22" stroke-width=".35"/>')
    for path in data['paths']:
        pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in xy[path])
        items.append(f'<polyline points="{pts}" fill="none" stroke="#21667f" stroke-width="2.8"/>')
    desc=escape(data.get('description',name))
    (OUT/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 410" role="img"><title>{desc}</title><rect width="640" height="410" fill="#f7fafb"/>'+''.join(items)+'</svg>\n')


def curve(name, points, **meta):
    return save(name, points, paths=[list(range(len(points)))], flat=True, **meta)


def integrate(fun, span, y0, **kw):
    return solve_ivp(fun,span,y0,rtol=2e-11,atol=2e-12,dense_output=True,method='DOP853',**kw)


def main():
    theta=np.linspace(0,2*np.pi,49)
    phi=np.linspace(0,np.pi,29)
    surface('sphere',lambda t,p:(2*math.sin(p)*math.cos(t),2*math.sin(p)*math.sin(t),2*math.cos(p)),theta,phi,description='Exact round shrinking sphere of radius 2 in R3.',status='formula')
    surface('cylinder',lambda t,z:(math.sqrt(2)*math.cos(t),math.sqrt(2)*math.sin(t),z),theta,np.linspace(-3,3,31),description='Exact shrinking cylinder of radius sqrt(2), shown in a finite axial window.',status='formula')
    surface('plane',lambda x,y:(x,y,0),np.linspace(-3,3,18),np.linspace(-3,3,18),description='A finite patch of a stationary plane.',status='formula')
    for a,name in [(0,'grim-reaper'),(.65,'tilted-grim')]:
        A=1+a*a
        surface(name,lambda x,y:(x,y,-A*math.log(math.cos(x/math.sqrt(A)))+a*y),np.linspace(-1.44*math.sqrt(A),1.44*math.sqrt(A),55),np.linspace(-2,2,21),description='Exact translator graph, truncated before its infinite ends.',status='formula',parameter=a)
    surface('clifford',lambda u,v:(math.sqrt(2)*math.cos(u),math.sqrt(2)*math.sin(u),math.sqrt(2)*math.cos(v),math.sqrt(2)*math.sin(v)),theta,theta,description='Linear projection of the exact Clifford torus in R4; overlaps are projection artifacts.',status='projection')
    surface('catenoid',lambda t,v:(math.cosh(v)*math.cos(t),math.cosh(v)*math.sin(t),v),theta,np.linspace(-1.65,1.65,45),description='Exact stationary catenoid, truncated at both ends.',status='formula')
    eps=1e-5
    sol=integrate(lambda r,y:[y[1],(1+y[1]**2)*(1-y[1]/r)],(eps,5),[eps**2/4+eps**4/128,eps/2+eps**3/32])
    r=np.linspace(eps,5,75); f,p=sol.sol(r)
    revolution('bowl',np.column_stack([np.r_[0,f],np.r_[0,r]]),description='Numerically integrated unit-speed rotational bowl translator; finite radius 5.',status='numerical-ode')
    AUDIT['bowl']={'equation':'f prime=p; p prime=(1+p^2)(1-p/r)','tip_expansion':'f=r^2/4+r^4/128+O(r^6)','radius':5,'rtol':2e-11}
    def tcat(s,y):
        r,z,a=y
        return [math.cos(a),math.sin(a),math.cos(a)-math.sin(a)/r]
    pieces=[]
    for sign in [-1,1]:
        sol=integrate(tcat,(0,sign*9),[1,0,np.pi/2])
        values=sol.sol(np.linspace(0,sign*9,100)).T
        pieces.append(values[::-1] if sign<0 else values[1:])
    values=np.concatenate(pieces)
    revolution('translating-catenoid',np.column_stack([values[:,1],values[:,0]]),description='Numerical translating catenoid with neck radius 1; both ends truncated.',status='numerical-ode')
    AUDIT['translating-catenoid']={'equation':"r'=cos(alpha); z'=sin(alpha); alpha'=cos(alpha)-sin(alpha)/r",'initial':[1,0,float(np.pi/2)],'arc_length_window':[-9,9]}
    def half_torus(R):
        def fun(s,y):
            x,r,a=y
            return [math.cos(a),math.sin(a),(1/r-r/2)*math.cos(a)+(x/2)*math.sin(a)]
        def crossing(s,y):return y[0]
        crossing.direction=-1;crossing.terminal=True
        sol=integrate(fun,(0,20),[0,R,0],events=crossing,max_step=.04)
        if not len(sol.t_events[0]): raise ValueError('Missing torus return')
        return sol
    R=brentq(lambda R:half_torus(R).y_events[0][0][2]+np.pi,3.30,3.33,xtol=1e-12)
    sol=half_torus(R); end=sol.t_events[0][0]
    v=sol.sol(np.linspace(0,end,100)).T
    half=v[:,:2]
    profile=np.concatenate([half,half[-2::-1]*np.array([-1,1])])
    revolution('angenent-torus',profile,description='Numerical closed rotational shrinker profile; a shooting approximation of an Angenent torus, not a circular torus.',status='numerical-ode',view={'pitch':.79})
    AUDIT['angenent-torus']={'equation':"x'=cos(alpha); r'=sin(alpha); alpha'=(1/r-r/2)cos(alpha)+(x/2)sin(alpha)",'outer_radius':float(R),'inner_radius':float(v[-1,1]),'half_length':float(end),'return_angle_error':float(abs(v[-1,2]+np.pi)),'return_position_error':float(abs(v[-1,0])),'normalization':'Hvec=-Xperp/2','proof_status':'numerical illustration only'}
    # Positive support function for the (m,n)=(2,3) Abresch--Langer curve.
    def al_period(a):
        def fun(t,y):return [y[1],2/y[0]-y[0]]
        def maximum(t,y):return y[1]
        maximum.direction=-1;maximum.terminal=True
        small=1e-6; dd=2/a-a
        sol=integrate(fun,(small,10),[a+.5*dd*small**2,dd*small],events=maximum,max_step=.025)
        return float(sol.t_events[0][0])
    a=brentq(lambda a:al_period(a)-4*np.pi/3,1.5,8,xtol=1e-12)
    sol=integrate(lambda t,y:[y[1],2/y[0]-y[0]],(0,4*np.pi),[a,0],max_step=.02)
    t=np.linspace(0,4*np.pi,801);h,hp=sol.sol(t)
    points=np.column_stack([h*np.cos(t)-hp*np.sin(t),h*np.sin(t)+hp*np.cos(t),np.zeros(len(t))])
    curve('abresch-langer',points,description='Numerical Abresch--Langer curve with turning number 2 and three support-function periods.',status='numerical-ode')
    AUDIT['abresch-langer']={'equation':"h''+h=2/h; X=h(cos theta,sin theta)+h'(-sin theta,cos theta)",'turning_number':2,'oscillations':3,'support_maximum':float(a),'period_error':float(abs(al_period(a)-4*np.pi/3)),'closure_error':float(np.linalg.norm(points[0]-points[-1]))}
    surface('al-cylinder',lambda i,z:(points[int(i)][0],points[int(i)][1],z),range(0,801,4),np.linspace(-2.5,2.5,17),description='Product of a numerical immersed Abresch--Langer curve with a line; finite axial window.',status='numerical-ode')
    # Expanders in the normalization Hvec=Xperp/2.
    sol=integrate(lambda r,y:[y[1],(1+y[1]**2)*((y[0]-r*y[1])/2-y[1]/r)],(eps,6),[1+eps**2/8,eps/4])
    r=np.linspace(eps,6,81); f,p=sol.sol(r)
    profile=np.column_stack([np.r_[1,f],np.r_[0,r]])
    revolution('expanding-graph',profile,description='Numerical entire rotational graphical expander with tip height 1, truncated at radius 6.',status='numerical-ode')
    top=revolution('two-sheet-expander',profile,description='Two disjoint reflected graphical expander sheets; numerical rotational example.',status='numerical-ode')
    vertices=top['vertices']+[[x,y,-z] for x,y,z in top['vertices']]
    faces=top['faces']+[[i+len(top['vertices']) for i in face] for face in top['faces']]
    save('two-sheet-expander',vertices,faces=faces,description=top['description'],status='numerical-ode')
    AUDIT['expanding-graph']={'equation':"f'=p; p'=(1+p^2)((f-rp)/2-p/r)",'tip_height':1,'tip_expansion':'f=1+r^2/8+O(r^4)','radius':6}
    sol=integrate(lambda x,y:[y[1],(1+y[1]**2)*(1/y[0]+(y[0]-x*y[1])/2)],(0,5),[.8,0])
    x=np.linspace(0,5,91); r,p=sol.sol(x)
    profile=np.column_stack([np.r_[-x[:0:-1],x],np.r_[r[:0:-1],r]])
    revolution('one-sheet-expander',profile,description='Numerical annular one-sheet expander with neck radius 0.8; finite axial window.',status='numerical-ode')
    AUDIT['one-sheet-expander']={'equation':"u''=(1+u'^2)(1/u+(u-xu')/2)",'neck_radius':.8,'axial_window':[-5,5],'critical_angle_claim':None}
    sol=integrate(lambda x,y:[y[1],(1+y[1]**2)*(y[0]-x*y[1])/2],(0,6),[1,0])
    x=np.linspace(0,6,160);f,p=sol.sol(x)
    curve('expanding-corner',np.column_stack([np.r_[-x[:0:-1],x],np.r_[f[:0:-1],f],np.zeros(319)]),description='Numerical convex self-expanding curve smoothing a corner; finite window.',status='numerical-ode')
    AUDIT['expanding-corner']={'equation':"f''=(1+f'^2)(f-xf')/2",'initial':[1,0],'window':[-6,6]}
    t=-2.;Y=np.arccosh(np.exp(-t)); y=np.linspace(-Y,Y,221);x=np.arccos(np.clip(np.exp(t)*np.cosh(y),-1,1))
    points=np.column_stack([np.r_[x,-x[::-1]],np.r_[y,y[::-1]],np.zeros(442)])
    curve('ancient-oval',points,description='Exact planar ancient oval cos(x)=exp(t) cosh(y), shown at t=-2.',status='formula',dynamic={'kind':'ancient-oval','min':-5,'max':-.1,'value':-2})
    u=np.linspace(0,2*np.pi,501)
    curve('whitney-profile',np.column_stack([np.sin(u)/(1+np.cos(u)**2),np.sin(u)*np.cos(u)/(1+np.cos(u)**2),np.zeros(len(u))]),description='Exact initial generating profile of the Whitney sphere; not its time-evolved geometry or an R3 embedding.',status='formula')
    (OUT/'geometry-audit.json').write_text(json.dumps(AUDIT,indent=2)+'\n')
    print(json.dumps(AUDIT,indent=2))

if __name__=='__main__':main()
