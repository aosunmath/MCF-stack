"""Minimal-cone ODE profiles and a regularized, finite-domain MCF experiment.

Run with Python + NumPy + SciPy + Matplotlib. No paper PDFs are exported.
The PDE runs are not the degree-selected Velazquez solutions.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'


def minimal_profile(p=4, q=4, radius=40., tol=1e-11):
    """Q(0)=1; the even Taylor expansion removes the apparent axis pole."""
    eps = 1e-5
    a = (q-1)/(2*p)
    b = (8*a**3-(q-1)*a)/(4*(p+2))
    def rhs(r, y):
        v, d = y
        return [d, (1+d*d)*((q-1)/v-(p-1)*d/r)]
    sol = solve_ivp(rhs, (eps, radius), [1+a*eps**2+b*eps**4, 2*a*eps+4*b*eps**3],
                    method='DOP853', rtol=tol, atol=tol/20, dense_output=True, max_step=max(.2, radius/100))
    if not sol.success:
        raise RuntimeError(sol.message)
    def evaluate(r):
        r = np.asarray(r)
        result = sol.sol(np.maximum(r, eps))
        small = r < eps
        result[0] = np.where(small, 1+a*r*r+b*r**4, result[0])
        result[1] = np.where(small, 2*a*r+4*b*r**3, result[1])
        return result
    return evaluate


def derivatives(r, u):
    """Second-order three-point formulas on a quadratic radial grid."""
    left, right = r[1:-1]-r[:-2], r[2:]-r[1:-1]
    d = -right/(left*(left+right))*u[:-2] + (right-left)/(left*right)*u[1:-1] + left/(right*(left+right))*u[2:]
    dd = 2*(u[:-2]/(left*(left+right))-u[1:-1]/(left*right)+u[2:]/(right*(left+right)))
    return d, dd


def operator(r, u, p=4, q=4):
    d, dd = derivatives(r, u)
    out = np.empty(len(u)-1)
    # At the smooth axis Q_r/r -> Q_rr, hence p Q_rr - (q-1)/Q.
    out[0] = p*2*(u[1]-u[0])/r[1]**2-(q-1)/u[0]
    out[1:] = dd/(1+d*d)+(p-1)*d/r[1:-1]-(q-1)/u[1:-1]
    return out


def pde_run(n=400, rounding=.02, radius=5., amplitude=.2, end=.5, rtol=2e-7):
    r = radius*np.linspace(0, 1, n+1)**2
    # Initial trace Q0=r+K r^6/(1+r^6), k=4 in ADS (1.1.1).
    # Replace the singular cone by its smooth minimal leaf at scale epsilon.
    leaf = minimal_profile(radius=radius/rounding+1)
    u0 = rounding*leaf(r/rounding)[0] + amplitude*r**6/(1+r**6)
    boundary = u0[-1]
    def rhs(t, u):
        return operator(r, np.r_[u, boundary])
    times = np.r_[0., np.geomspace(.001, end, 45)]
    sol = solve_ivp(rhs, (0, end), u0[:-1], method='BDF', t_eval=times,
                    rtol=rtol, atol=rtol/50, jac_sparsity=diags([np.ones(n-1),np.ones(n),np.ones(n-1)], [-1,0,1]), max_step=.01)
    if not sol.success or np.min(sol.y) <= 0:
        raise RuntimeError('PDE integration failed: '+sol.message)
    values = np.vstack([sol.y, np.full(len(times), boundary)]).T
    return r, times, values, {'steps_rhs':sol.nfev, 'jacobians':sol.njev, 'rtol':rtol, 'atol':rtol/50}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    profiles=[]
    for p,q in [(4,4),(5,5),(6,6),(3,5)]:
        r=np.r_[0.,np.geomspace(.001,20000,1400)]
        f=minimal_profile(p,q,radius=20000)
        u,d=f(r)
        fine=minimal_profile(p,q,radius=20000,tol=2e-13)(r)[0]
        profiles.append({'p':p,'q':q,'r':r.tolist(),'u':u.tolist(),'slope':d.tolist(),
                         'refinement_error':float(np.max(abs(u-fine))), 'cone_slope':float(np.sqrt((q-1)/(p-1)))})
    runs=[]
    for n,eps,L in [(240,.02,5.),(480,.02,5.),(480,.01,5.),(480,.005,5.),(672,.01,7.)]:
        r,t,u,info=pde_run(n,eps,L)
        runs.append((r,t,u))
        print('PDE',n,eps,L,'axis',u[-1,0],flush=True)
    r,t,u=runs[2]
    grid_error=float(np.max(abs(runs[0][2]-np.array([np.interp(runs[0][0],runs[1][0],v) for v in runs[1][2]]))))
    mask=r<=2
    boundary_error=float(np.max(abs(u[:,mask]-np.array([np.interp(r[mask],runs[4][0],v) for v in runs[4][2]]))))
    regularization_error=float(np.max(abs(u[-1]-runs[3][2][-1])))
    # Independent stationary-leaf and exact-cylinder checks exercise the axis treatment.
    residuals=[]
    for n in [120,240,480]:
        rr=5*np.linspace(0,1,n+1)**2
        residuals.append(float(np.max(abs(operator(rr,minimal_profile()(rr)[0])))))
    audit={'method':'DOP853 minimal ODE; method of lines, quadratic radial grid, sparse BDF for nonlinear PDE',
           'pde_equation':'Q_t=Q_rr/(1+Q_r^2)+3 Q_r/r-3/Q',
           'domain':[0,5], 'time':[0,.5], 'initial_rounding':.01, 'amplitude':.2,
           'initial_data':'epsilon Q_1(r/epsilon)+0.2 r^6/(1+r^6)',
           'boundary':'Q_r(0,t)=0; fixed Q(5,t)=Q(5,0)',
           'stationary_leaf_residuals_120_240_480':residuals,
           'grid_240_480_max_error_all_times':grid_error,
           'domain_5_7_max_error_r_le_2':boundary_error,
           'rounding_001_0005_final_max_error':regularization_error,
           'run_final_axis':{str(params):float(v[2][-1,0]) for params,v in zip([(240,.02,5),(480,.02,5),(480,.01,5),(480,.005,5),(672,.01,7)],runs)},
           'primary_final_axis':float(u[-1,0]),
           'claims':'Finite-domain regularized forward PDE only. No convergence proof at the singular trace, critical-data tuning, certified type-II rate, or entropy computation.'}
    data={'profiles':profiles,'pde':{'r':r[::2].tolist(),'times':t.tolist(),'values':u[:,::2].tolist(),
           'axis':u[:,0].tolist(),'rounding':.01,'amplitude':.2,'domain':5},'audit':audit}
    (OUT/'simons-cone-experiment.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'simons-cone-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    for model,scenario,p,q in [('low-mode','low',5,5),('bounded','bounded',4,4),('compact','compact',3,5),('smoothing','pde',4,4)]:
        profile=next(item for item in profiles if item['p']==p and item['q']==q)
        vertices=([[float(x),float(y),0] for x,y in zip(r,u[0])] if scenario=='pde'
                  else [[x,y,0] for x,y in zip(profile['r'],profile['u'])])
        stub={'kind':'simons-cone-profile','scenario':scenario,
              'status':'numerical-pde' if scenario=='pde' else 'numerical-ode',
              'vertices':vertices,'faces':[],'paths':[list(range(len(vertices)))],
              'description':'Orbit profile; full time and scale data in simons-cone-experiment.json.'}
        (OUT/('simons-cone-'+model+'.json')).write_text(json.dumps(stub,separators=(',',':'))+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans'})
    for name,title,p,q,mode in [
        ('simons-cone-low-mode','Type-II cone singularity: two spatial scales',5,5,'shrink'),
        ('simons-cone-bounded','Bounded mean curvature: a minimal inner model',4,4,'shrink'),
        ('simons-cone-compact','Compact Lawson-cone singularity: local profile',3,5,'shrink'),
        ('simons-cone-smoothing','After the cone singularity: nonlinear PDE experiment',4,4,'pde')]:
        fig,ax=plt.subplots(figsize=(8,5.1),layout='constrained')
        fig.patch.set_facecolor('#f8fafc'); ax.set_facecolor('#f8fafc')
        x=np.linspace(0,2,500); mu=np.sqrt((q-1)/(p-1))
        ax.plot(x,mu*x,'--',color='#64748b',label='Minimal cone')
        if mode=='pde':
            for ti in [0,20,35,45]:ax.plot(r,u[ti],label=f't = {t[ti]:.3f}')
            ax.set(xlim=(0,1.5),ylim=(0,1.7))
            note='Regularized initial trace; finite radial domain. Not a certified continuation.'
        else:
            f=minimal_profile(p,q,radius=100)
            for b in [.55,.25,.08]:ax.plot(x,b*f(x/b)[0],label=f'Inner scale b = {b:g}')
            ax.set(xlim=(0,2),ylim=(0,2.6 if p!=q else 2.1))
            note='Numerical minimal ODE + asymptotic scaling; these dilations are not MCF.'
        ax.set_title(title,pad=14,fontsize=13)
        ax.set_xlabel(f'r = |x| in R^{p}');ax.set_ylabel(f'Q = |y| in R^{q}')
        ax.legend(loc='upper left',fontsize=9);ax.grid(alpha=.18)
        fig.text(.5,.005,note,ha='center',fontsize=8)
        fig.savefig(OUT/(name+'.svg'));plt.close(fig)
    print(json.dumps(audit,indent=2))


if __name__=='__main__':
    main()
