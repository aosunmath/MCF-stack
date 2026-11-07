"""Apex-curvature comparison: exact grim, audited PDE wing, numerical ODE bowl.

Requires NumPy, SciPy and Matplotlib only when regenerating the assets.
The wing reuses generate_delta_wing.py's committed computation, not a formula
fitted to its Hessian. No interpolation between distinct translators is used.
"""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'


def bowl_solution(eps=1e-5, tol=2e-11):
    return solve_ivp(lambda r, u: [u[1], (1+u[1]**2)*(1-u[1]/r)],
                     (eps, 6), [eps**2/4+eps**4/128, eps/2+eps**3/32],
                     method='DOP853', rtol=tol, atol=tol/10, dense_output=True)


def radial_mesh(solution):
    angles=np.arange(192)*2*np.pi/192
    radii=[brentq(lambda r: solution.sol(r)[0]-z, .01, 6) for z in np.linspace(0,6,49)[1:]]
    vertices=[[0,0,0]];normals=[[0,0,1]]
    for r in radii:
        z,p=solution.sol(r)
        for a in angles:
            vertices.append([r*np.cos(a),r*np.sin(a),z])
            normals.append(np.array([-p*np.cos(a),-p*np.sin(a),1])/np.sqrt(1+p*p))
    return vertices,normals


def grim_mesh():
    xs=np.linspace(-8,8,65)
    # Parameterize the steep ends by height, with a regular coordinate at y=0.
    z=np.linspace(-np.sqrt(6),np.sqrt(6),97)
    ys=np.sign(z)*np.arccos(np.exp(-z*z))
    v=[[x,y,-np.log(np.cos(y))] for x in xs for y in ys]
    n=[[0,-np.sin(y),np.cos(y)] for x in xs for y in ys]
    faces=[]
    for i in range(64):
        for j in range(96):
            a=i*97+j;faces.extend([[a,a+97,a+98],[a,a+98,a+1]])
    paths=[[i*97+j for i in range(65)] for j in [0,16,24,32,64,72,80,96]]
    symmetry=[[i*97+48 for i in range(65)],list(range(32*97,33*97))]
    return dict(vertices=v,normals=n,faces=faces,paths=paths,symmetryPaths=symmetry)


def rounded(data):
    for key in ['vertices','normals','profiles']:
        data[key]=np.round(data[key],8).tolist() if key!='profiles' else [np.round(p,8).tolist() for p in data[key]]
    return data


def generate():
    wing=json.loads((OUT/'delta-wing.json').read_text())
    wing_audit=json.loads((OUT/'delta-wing-audit.json').read_text())
    symmetry=[[0]+[1+i*192+a for i in range(48)] for a in [0,48,96,144]]
    profiles=[wing['longitudinal'],wing['sections'][0]]
    common=dict(maxHeight=6,ambient='R3',velocity=[0,0,1])
    data={**common,**{k:wing[k] for k in ['vertices','normals','faces','paths']},
          'name':'apex-ellipsoid','kind':'apex-translators','status':'numerical-pde',
          'label':'Δ-wing','curvatures':wing_audit['apex_hessian'],
          'curvatureLabel':'k₁ ≈ 0.2443, k₂ ≈ 0.7557',
          'method':'Numerical PDE','domain':'ℝ × (−π/√2, π/√2)',
          'note':'Apex values are measured from the finite-domain computation; no exact width-to-curvature formula is asserted.',
          'description':'Three surface cases in R3: grim-reaper cylinder, numerical Delta-wing and numerical bowl, with apex sections.',
          'symmetryPaths':symmetry,'profiles':profiles}
    xs=np.linspace(-8,8,401);ys=np.linspace(-1.5,1.5,401)
    grim={**common,**grim_mesh(),'label':'Grim-reaper cylinder','status':'formula',
          'curvatures':[0,1],'curvatureLabel':'k₁ = 0, k₂ = 1',
          'method':'Exact formula','domain':'ℝ × (−π/2, π/2)',
          'note':'u(x,y) = −log cos y. The minimum is a whole straight line; x is truncated to |x| ≤ 8.',
          'profiles':[np.column_stack([xs,np.zeros_like(xs)]),np.column_stack([ys,-np.log(np.cos(ys))])]}
    sol=bowl_solution();fine=bowl_solution(5e-6,2e-12)
    v,n=radial_mesh(sol);rmax=np.hypot(*v[-1][:2]);ts=np.linspace(-rmax,rmax,401)
    z=sol.sol(np.maximum(abs(ts),1e-5))[0];z[len(ts)//2]=0
    bowl={**common,'vertices':v,'normals':n,'faces':wing['faces'],'paths':wing['paths'],
          'symmetryPaths':symmetry,'label':'Rotational bowl','status':'numerical-ode',
          'curvatures':[.5,.5],'curvatureLabel':'k₁ = k₂ = ½',
          'method':'Numerical ODE','domain':'ℝ²',
          'note':'Equal curvatures give rotational symmetry. The plotted profile solves the bowl ODE numerically.',
          'profiles':[np.column_stack([ts,z]),np.column_stack([ts,z])]}
    data['cases']={'grim':rounded(grim),'bowl':rounded(bowl)}
    audit=dict(source='https://arxiv.org/abs/1805.10860v2',
        source_locations='Equations (1.2)–(1.4), Figure 3, Sections 3–4, Theorem 7.1, Theorem 8.1 and Corollary 8.2',
        normalization='Upward unit speed, u(0)=0, positive apex Hessian eigenvalues; M_t=graph(u)+t e3, t in R.',
        scope='Three R3 representatives only; not a rendering of the higher-dimensional family or a continuous computed family.',
        delta_wing=dict(asset='delta-wing.json',sha256=hashlib.sha256((OUT/'delta-wing.json').read_bytes()).hexdigest(),
            audit='delta-wing-audit.json',apex_hessian=wing_audit['apex_hessian'],
            max_sampled_interpolant_pde_residual=wing_audit['max_sampled_interpolant_pde_residual'],
            domain_comparison=wing_audit['domain_comparison'],grid_comparison=wing_audit['grid_comparison']),
        bowl=dict(equation="f'=p, p'=(1+p^2)(1-p/r)",tip_expansion='f=r^2/4+r^4/128+O(r^6)',
                  epsilon=1e-5,rtol=2e-11,atol=2e-12,display_max_height=6,
                  comparison=dict(epsilon=5e-6,rtol=2e-12,
                      max_height_change=float(max(abs(sol.sol(np.linspace(.01,rmax,1000))[0]-fine.sol(np.linspace(.01,rmax,1000))[0]))))),
        limitations='Floating-point diagnostics, not certified bounds. All surfaces are truncated. The dashed quadratic in section view is local Taylor data, not a global translator.')
    (OUT/'apex-ellipsoid.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'apex-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    drawing(data)


def drawing(data):
    os.environ.setdefault('MPLCONFIGDIR','/tmp/mcf-apex-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'mcf-apex',
        'font.family':'DejaVu Sans','font.size':10,'text.color':'#183f52','axes.labelcolor':'#183f52'})
    fig=plt.figure(figsize=(11,7),facecolor='#f7fafb')
    fig.text(.04,.945,'From a flat direction to a round apex',fontsize=22,weight='bold')
    fig.text(.04,.90,'Three members in ℝ³ · upward speed 1 · nonnegative apex curvatures sum to 1',fontsize=12)
    for col,d in enumerate([data['cases']['grim'],data,data['cases']['bowl']]):
        left=.035+col*.325
        fig.text(left,.835,d['label'],fontsize=14,weight='bold')
        fig.text(left,.802,d['curvatureLabel'],fontsize=11)
        ax=fig.add_axes([left-.035,.43,.345,.37],projection='3d',facecolor='#f7fafb')
        v=np.array(d['vertices']);f=np.array(d['faces']);centers=v[f].mean(axis=1)
        # A half-cut keeps the apex and its two symmetry sections visible.
        f=f[centers[:,1]>=0];centers=v[f].mean(axis=1)
        colors=np.tile(np.array([87,155,171])/255,(len(f),1))
        colors[np.mod(centers[:,2],1)>.88]*=.73
        poly=Poly3DCollection(v[f],facecolors=colors,linewidths=0,antialiased=False,shade=True,rasterized=True)
        ax.add_collection3d(poly)
        for path in d['symmetryPaths']:
            p=v[path];p=p[p[:,1]>=-1e-8]
            if len(p)>1:ax.plot(*p.T,color='#c8893c' if np.max(abs(p[:,0]))<1e-7 else '#174d70',lw=1.7)
        ax.scatter([0],[0],[0],s=12,color='#183f52',depthshade=False)
        ax.set(xlim=(-8,8),ylim=(-4,4),zlim=(-.5,6.5));ax.set_box_aspect([16,8,7]);ax.view_init(elev=31,azim=-61);ax.set_axis_off()
        fig.text(left,.425,d['method']+' · '+('flat minimum line' if col==0 else 'isolated minimum'),fontsize=9.5)
        a=fig.add_axes([left+.035,.17,.245,.19],facecolor='#f7fafb')
        for i,(line,color) in enumerate(zip(d['profiles'],['#21667f','#bc7b32'])):
            p=np.array(line);p=p[abs(p[:,0])<=2]
            a.plot(*p.T,color=color,lw=2,label='x section' if i==0 else 'y section')
            t=np.linspace(-1,1,101);a.plot(t,.5*d['curvatures'][i]*t*t,'--',color=color,lw=1)
        a.set(xlim=(-2,2),ylim=(-.08,2.4),xlabel='Distance from the apex',ylabel='Height')
        a.spines[['top','right']].set_visible(False);a.spines[['bottom','left']].set_color('#a7bbc4');a.tick_params(colors='#526b77',labelsize=8);a.grid(alpha=.12)
    fig.text(.04,.095,'Principal sections: blue along x, ochre along y. Dashed: local quadratic data.',fontsize=11)
    fig.text(.04,.05,'Half-cut views; all rim edges are display cuts. Numerical curves have no certified error bounds.',fontsize=10,color='#526b77')
    fig.savefig(OUT/'apex-ellipsoid.svg',dpi=160,metadata={'Date':None})
    p=OUT/'apex-ellipsoid.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
    fig.savefig(OUT/'apex-ellipsoid.png',dpi=160);plt.close(fig)


if __name__=='__main__':generate()
