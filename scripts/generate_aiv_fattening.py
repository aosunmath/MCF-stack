"""Reproduce AIV orbit-space ODE experiments (no private paper required).

Run with Python, NumPy, SciPy and Matplotlib. Outputs are numerical, not
interval-certified. The R8 time model is explicitly only an inner asymptotic.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root, brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
TOL = 2e-11


def rhs(x, state, p, q, sign):
    u, v = state
    return np.array([v, (1+v*v)*((q-1)/u-(p-1)*v/x+sign*(u-x*v)/2)])


def axis(a, p, q, sign, end, tol=TOL, epsilon_factor=1e-4):
    epsilon = min(a*epsilon_factor, 1e-5)
    second = ((q-1)/a+sign*a/2)/p
    result = solve_ivp(lambda x, y: rhs(x, y, p, q, sign), (epsilon, end),
                       [a+second*epsilon**2/2, second*epsilon],
                       method='DOP853', rtol=tol, atol=tol/100, dense_output=True)
    if not result.success:
        raise ValueError(result.message)
    return result


def asymptotic(A, p, q, sign):
    B = sign*((p-1)*A-(q-1)/A)
    C = sign*B/3*(2/(1+A*A)-(p-1)+(q-1)/A**2)
    return B, C


def inward(A, p, q, cutoff, match=1.5, tol=TOL):
    B, C = asymptotic(A, p, q, -1)
    result = solve_ivp(lambda x,y: rhs(x,y,p,q,-1), (cutoff, match),
                      [A*cutoff+B/cutoff+C/cutoff**3,
                       A-B/cutoff**2-3*C/cutoff**4],
                      method='DOP853',rtol=tol,atol=tol/100,dense_output=True)
    if not result.success:
        raise ValueError(result.message)
    return result


def shrinker(guess, cutoff=32, tol=TOL):
    def residual(z):
        a, A = np.exp(z)
        return axis(a,2,2,-1,1.5,tol).y[:,-1]-inward(A,2,2,cutoff,tol=tol).y[:,-1]
    shot = root(residual,np.log([guess,1.0]),tol=1e-9)
    if np.max(abs(residual(shot.x))) > 2e-8:
        raise ValueError('Shrinker matching did not converge')
    a, A = np.exp(shot.x)
    left=axis(a,2,2,-1,1.5,tol);right=inward(A,2,2,cutoff,tol=tol)
    x=np.unique(np.r_[0,np.geomspace(a*1e-4,1.5,650),np.linspace(1.5,cutoff,800)])
    y=np.where(x<1.5,left.sol(np.maximum(x,left.t[0]))[0],right.sol(np.maximum(x,1.5))[0]);y[0]=a
    return dict(a=float(a),slope=float(A),x=x,y=y,match=float(np.max(abs(residual(shot.x)))))


def cone_slope(sol, p, q, cutoff):
    u,v=sol.y[:,-1]
    A=(u/cutoff+v)/2
    # Cancel the leading B/r^2 and C/r^4 contamination in u/r.
    _,C=asymptotic(A,p,q,1)
    return float(A+C/cutoff**4)


def expander_slope(a,p,q,cutoff=32,tol=TOL):
    return cone_slope(axis(a,p,q,1,cutoff,tol),p,q,cutoff)


def points(sol,a,end,swap=False):
    x=np.unique(np.r_[0,np.geomspace(max(a*1e-4,1e-8),end,1050)])
    y=sol.sol(np.maximum(x,sol.t[0]))[0];y[0]=a
    return np.column_stack((y,x) if swap else (x,y)).round(11).tolist()


def scaled_difference(first,second):
    return float(np.max(abs(np.interp(first['x'],second['x'],second['y'])-first['y'])))


def ode_defect(sol,p,q,sign):
    # Independent centered derivative of the dense interpolant, not RHS-RHS.
    x=np.geomspace(max(sol.t[0]*100,0.03),min(12,sol.t[-1])-.002,250)
    h=np.minimum(1e-5*x,1e-4)
    y=sol.sol(x); derivative=(sol.sol(x+h)[1]-sol.sol(x-h)[1])/(2*h)
    expected=np.array([rhs(xx,yy,p,q,sign)[1] for xx,yy in zip(x,y.T)])
    return float(np.max(abs(derivative-expected)/(1+abs(expected))))


def generate():
    diagnostic={'method':'DOP853; axis Taylor regularization; two-sided shrinker shooting; Brent expander matching',
                'rtol':TOL,'refined_rtol':2e-13,'certified':False,
                'limitation':'Cutoff/tolerance comparisons are numerical diagnostics, not rigorous error bounds or a fattening proof.'}
    shr=[]
    for m,guess in [(2,.109),(3,.01017)]:
        s=shrinker(guess); refined=shrinker(s['a'],40,2e-13)
        check=shrinker(s['a'],32,2e-13)
        curves=np.column_stack((refined['x'],refined['y'])).round(11).tolist()
        # Count crossings in a resolved logarithmic grid; not a proof at infinity.
        deviations=refined['y']-refined['x']
        rec=dict(name=f'm = {m}',p=2,q=2,m=m,a=refined['a'],slope=refined['slope'],points=curves,
                 diagnostics=dict(axis_radius_cutoff_change=abs(refined['a']-check['a']),
                    cone_slope_cutoff_change=abs(refined['slope']-check['slope']),
                    cone_slope_tolerance_change=abs(s['slope']-check['slope']),
                    matching_residual=refined['match'],
                    resolved_minimal_cone_crossings=int(np.sum(deviations[1:]*deviations[:-1]<0))))
        shr.append(rec)
    target=shr[1]['slope'];continuations=[]
    # Two cap radii on the same side and one on the exchanged-block side.
    for name,bracket,swap in [('Small y-cap',(.04,.12),False),('Large y-cap',(.5,.8),False),('x-cap',(.5,.9),True)]:
        goal=1/target if swap else target
        a=brentq(lambda a:expander_slope(a,2,2,32)-goal,*bracket,xtol=2e-12)
        finer=brentq(lambda a:expander_slope(a,2,2,40,2e-13)-goal,*bracket,xtol=1e-13)
        sol=axis(finer,2,2,1,40,2e-13)
        raw=cone_slope(sol,2,2,40);slope=1/raw if swap else raw
        continuations.append(dict(name=name,a=float(finer),p=2,q=2,swap=swap,slope=slope,points=points(sol,finer,40,swap),
            diagnostics=dict(radius_refinement_change=abs(finer-a),cone_slope_mismatch=abs(slope-target),
                ode_relative_defect=ode_defect(sol,2,2,1))))
    data={'shrinkers':shr,'continuations':continuations,'matched_shrinker_index':1,'expanders':[],'minimal':[]}
    # Fully recorded dimensions; no interpolation between distinct ODE profiles.
    for p,q in [(2,2),(2,3),(3,3),(3,4),(2,6),(6,2),(4,4)]:
        for a in [.03,.1,.3,1.0]:
            sol=axis(a,p,q,1,32);ref=axis(a,p,q,1,40,2e-13,5e-5)
            slope=cone_slope(ref,p,q,40)
            sample=np.geomspace(max(a*.001,.00001),16,300)
            data['expanders'].append(dict(name=f'({p}, {q}), a = {a:g}',p=p,q=q,a=a,slope=slope,
                points=points(ref,a,40),diagnostics=dict(cone_slope_refinement_change=abs(slope-cone_slope(sol,p,q,32)),
                profile_refinement_max=float(np.max(abs(sol.sol(sample)[0]-ref.sol(sample)[0]))),
                ode_relative_defect=ode_defect(ref,p,q,1))))
        sol=axis(1,p,q,0,40);ref=axis(1,p,q,0,40,2e-13,5e-5)
        sample=np.geomspace(.001,40,1200);dev=ref.sol(sample)[0]-np.sqrt((q-1)/(p-1))*sample
        data['minimal'].append(dict(name=f'({p}, {q})',p=p,q=q,a=1,points=points(ref,1,40),
             cone_slope=float(np.sqrt((q-1)/(p-1))),diagnostics=dict(profile_refinement_max=float(np.max(abs(sol.sol(sample)[0]-ref.sol(sample)[0]))),
             min_cone_deviation=float(np.min(dev)),min_deviation_x=float(sample[np.argmin(dev)]),ode_relative_defect=ode_defect(ref,p,q,0))))
    diagnostic['shrinkers']=[{k:v for k,v in s.items() if k!='points'} for s in shr]
    diagnostic['continuations']=[{k:v for k,v in s.items() if k!='points'} for s in continuations]
    diagnostic['expanders']=[{k:v for k,v in s.items() if k!='points'} for s in data['expanders']]
    diagnostic['minimal']=[{k:v for k,v in s.items() if k!='points'} for s in data['minimal']]
    n8=next(s for s in data['expanders'] if (s['p'],s['q'],s['a'])==(2,6,.1))
    diagnostic['r8_expander_slope_gap']=n8['slope']-np.sqrt(5)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'aiv-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'aiv-audit.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    figures(data)
    template=(ROOT/'scripts/templates/aiv.html').read_text().replace('__VIEWER__',(ROOT/'site/assets/aiv-viewer.mjs').read_text())
    for model in ['aiv-shrinkers','aiv-expanders','aiv-minimal','aiv-eight-fattening']:
        html=template.replace('__MODEL__',model).replace('__DATA__',json.dumps(data,separators=(',',':')))
        (ROOT/f'site/experiments/{model}.html').write_text(html)
    print(json.dumps({k:diagnostic[k] for k in ['shrinkers','continuations','r8_expander_slope_gap']},indent=2))


def figures(data):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
    colors=['#146c84','#d87930','#773bb0','#27825d']
    for model in ['aiv-shrinkers','aiv-expanders','aiv-minimal','aiv-eight-fattening']:
        fig,axes=plt.subplots(1,2,figsize=(9.6,5.6),layout='constrained')
        if model=='aiv-shrinkers':
            selected=[data['shrinkers'][1],*data['continuations']];A=selected[0]['slope'];limit=2
            title='A smooth shrinker and distinct expanding continuations'
            subtitle='Numerical ODE profiles in R4 · same cone slope A ≈ %.9f'%A
            for i,record in enumerate(selected):
                xy=np.array(record['points']);mask=xy[:,0]<=limit
                axes[0].plot(xy[mask,0],xy[mask,1],color=colors[i],label=('Shrinker at t = −1' if i==0 else record['name']+' at t = 1'))
                axes[1].plot(xy[mask,0],(xy[:,1]-A*xy[:,0])[mask],color=colors[i])
            axes[0].plot([0,limit],[0,A*limit],'--',color='#63727b',label='Common limiting cone')
        elif model=='aiv-expanders':
            selected=[s for s in data['expanders'] if s['p']==s['q']==2];A=1;limit=3
            title='Axis-starting self-expanders';subtitle='Numerical ODE · (p, q) = (2, 2) · profiles at t = 1'
            for i,record in enumerate(selected):
                xy=np.array(record['points']);mask=xy[:,0]<=limit
                axes[0].plot(xy[mask,0],xy[mask,1],color=colors[i],label=f'a = {record["a"]:g}, B ≈ {record["slope"]:.6f}')
                axes[1].plot(xy[mask,0],(xy[:,1]-xy[:,0])[mask],color=colors[i])
            axes[0].plot([0,limit],[0,limit],'--',color='#63727b',label='Minimal cone y = x')
        else:
            p,q=(2,2) if model=='aiv-minimal' else (2,6);A=np.sqrt((q-1)/(p-1));limit=8
            selected=[next(s for s in data['minimal'] if (s['p'],s['q'])==k) for k in [(p,q),(q,p)]]
            title='Stationary minimal caps' if model=='aiv-minimal' else 'Inner models at the Simoes cone in R8'
            subtitle='Numerical minimal ODE · cone crossings are not self-intersections' if model=='aiv-minimal' else 'Stationary ODE models only · no nonlinear type II flow is computed'
            for i,record in enumerate(selected):
                xy=np.array(record['points']);xy=xy[:,::-1] if i else xy;mask=xy[:,0]<=limit
                axes[0].plot(xy[mask,0],xy[mask,1],color=colors[i],label='y-cap' if i==0 else 'x-cap')
                axes[1].plot(xy[mask,0],(xy[:,1]-A*xy[:,0])[mask],color=colors[i])
            axes[0].plot([0,limit],[0,A*limit],'--',color='#63727b',label='Minimal cone')
        for ax in axes:
            ax.grid(alpha=.18);ax.set_xlabel('x = |X|');ax.set_xlim(0,limit)
        axes[0].set_ylabel('y = |Y|');axes[0].set_aspect('equal',adjustable='box');axes[0].legend(fontsize=8)
        axes[1].axhline(0,color='#63727b',linestyle='--');axes[1].set_ylabel('y − A x (cone deviation)')
        if model=='aiv-eight-fattening':axes[1].set_ylim(-.002,.004);axes[1].set_xlim(1,8)
        axes[1].set_title('Deviation enlarged; scales differ from left panel',fontsize=9)
        fig.suptitle(title+'\n'+subtitle,fontsize=12)
        fig.supxlabel('Orbit-space radii, not a surface in R3. Display endpoints are truncations.',fontsize=9)
        fig.savefig(OUT/(model+'.svg'));fig.savefig('/tmp/'+model+'.png',dpi=130);plt.close(fig)


if __name__=='__main__':
    generate()
