"""Numerical n=2 Whitney flow, in Viana's trace-mean-curvature normalization.

Run with Python + NumPy + SciPy. No supplied paper is copied into the site.
See documentation/whitney-flow-picture.md for the equation, gauge and limits.
"""
from pathlib import Path
import json
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
TIMES = np.linspace(0, .09, 91)
SNAPSHOTS = [0, 30, 60, 90]


def initial(intervals):
    u = np.linspace(0, np.pi / 2, intervals + 1)
    p = np.column_stack([np.sin(u) / (1 + np.cos(u)**2),
                         np.sin(u) * np.cos(u) / (1 + np.cos(u)**2)])
    p[0] = 0
    p[-1, 1] = 0
    return p


def velocity(t, flat):
    p = flat.reshape(-1, 2)
    h = np.pi / (2 * (len(p) - 1))
    # Odd extension at the double point; (x,-y) reflection at the outer tip.
    extended = np.vstack([-p[1], p, p[-2] * [1, -1]])
    du = (extended[2:] - extended[:-2]) / (2 * h)
    ddu = (extended[2:] - 2 * p + extended[:-2]) / h**2
    q = np.sum(du * du, axis=1)
    r2 = np.sum(p * p, axis=1)
    r2[0] = 1  # Endpoint velocity is exactly zero by odd symmetry.
    normal = np.column_stack([-du[:, 1], du[:, 0]])
    projected = normal * (np.sum(p * normal, axis=1) / q)[:, None]
    result = ddu / q[:, None] - projected / r2[:, None]
    result[0] = 0
    result[-1, 1] = 0
    return result.ravel()


def solve(intervals, times=TIMES, rtol=2e-9, atol=2e-11):
    p = initial(intervals)
    sparsity = lil_matrix((p.size, p.size))
    for i in range(intervals + 1):
        sparsity[2*i:2*i+2, max(0, 2*i-2):min(p.size, 2*i+4)] = 1
    result = solve_ivp(velocity, (0, float(times[-1])), p.ravel(),
                       method='BDF', t_eval=times, rtol=rtol, atol=atol,
                       jac_sparsity=sparsity.tocsr(), max_step=.0005)
    if not result.success or len(result.t) != len(times):
        raise RuntimeError(result.message)
    return result.y.T.reshape(-1, intervals + 1, 2)


def right_lobe(quarter):
    return np.vstack([quarter, quarter[-2::-1] * [1, -1]])


def profile(quarter):
    right = right_lobe(quarter)
    # The second lobe is redundant in the sphere parametrization.
    return np.vstack([right, -right[1:]])


def project_surface(quarter, segments=24):
    lobe = right_lobe(quarter)
    v = np.arange(segments) * 2*np.pi / segments
    c, s = np.cos(v), np.sin(v)
    p = np.array([[a*cj, a*sj, b*cj, b*sj] for a,b in lobe for cj,sj in zip(c,s)])
    x, y, z, w = p.T
    y = y*np.cos(.55)-w*np.sin(.55)
    horizontal = x*np.cos(.64)-y*np.sin(.64)
    depth = x*np.sin(.64)+y*np.cos(.64)
    q = np.column_stack([horizontal, z*np.cos(.43)-depth*np.sin(.43), z*np.sin(.43)+depth*np.cos(.43)])
    faces = []
    for i in range(len(lobe)-1):
        for j in range(segments):
            a=i*segments+j; b=i*segments+(j+1)%segments
            faces.extend([(a,b,b+segments,i), (a,b+segments,a+segments,i)])
    return q, sorted(faces, key=lambda f: sum(q[k,2] for k in f[:3]))


def svg(frames):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 610" role="img" aria-labelledby="title desc">',
             '<title id="title">Whitney two-sphere: four times on the same spatial scale</title>',
             '<desc id="desc">Exact initial data at t=0 and numerical equivariant mean curvature flow at t=0.03, 0.06 and 0.09. Each panel pairs an R4-to-R3 surface projection with its planar figure-eight profile. All dimensions use one spatial scale. Extra crossings can arise in projection; the true immersion has one double point at the origin.</desc>',
             '<rect width="800" height="610" fill="#f7fafb"/>',
             '<g font-family="system-ui,sans-serif" fill="#183f52">',
             '<text x="24" y="30" font-size="19" font-weight="600">Whitney sphere under mean curvature flow</text>',
             '<text x="24" y="52" font-size="13">n = 2 · surface in R⁴ · fixed spatial scale · positive times are numerical</text>']
    for k, index in enumerate(SNAPSHOTS):
        x=16+(k%2)*392; y=70+(k//2)*262; cx=x+188
        quarter=frames[index]
        parts.extend([f'<rect x="{x}" y="{y}" width="376" height="250" rx="6" fill="white" stroke="#d6e1e6"/>',
                      f'<text x="{x+14}" y="{y+24}" font-size="16" font-weight="600">t = {TIMES[index]:.3f}</text>',
                      f'<text x="{x+230}" y="{y+24}" font-size="12">{"Exact initial data" if index==0 else "Numerical flow"}</text>'])
        points, faces=project_surface(quarter[::4])
        scale=100
        for a,b,c,row in faces:
            normal=np.cross(points[b]-points[a],points[c]-points[a])
            light=.48+.45*abs(np.dot(normal,[.3,.5,.8]))/(np.linalg.norm(normal) or 1)
            base=np.array([43,139,159] if row<len(quarter[::4])-1 else [207,123,70])
            rgb=tuple(map(int,np.round(base*light+255*(1-light)*.32)))
            coords=' '.join(f'{cx+scale*points[i,0]:.2f},{y+104-scale*points[i,1]:.2f}' for i in [a,b,c])
            parts.append(f'<polygon points="{coords}" fill="rgb{rgb}" stroke="rgb{rgb}" stroke-width=".18"/>')
        parts.append(f'<circle cx="{cx}" cy="{y+104}" r="2.4" fill="#183f52"/><text x="{x+14}" y="{y+154}" font-size="11">R⁴ → R³ projection</text>')
        cy=y+196
        parts.append(f'<path d="M {cx-140} {cy} H {cx+140} M {cx} {cy-35} V {cy+35}" stroke="#d7e1e5"/>')
        for sign in [1,-1]:
            for q,color in [(quarter,'#21667f'),(quarter*[1,-1],'#b96934')]:
                coords=' '.join(f'{cx+94*sign*a:.3f},{cy-94*sign*b:.3f}' for a,b in q)
                parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="#183f52"/><text x="{x+14}" y="{y+241}" font-size="11">Planar generating profile</text>')
    parts.append('<text x="24" y="602" font-size="12">The flow is not self-similar. These snapshots stop before the singularity; t = 0.09 is not T.</text></g></svg>\n')
    return ''.join(parts)


def main():
    coarse=solve(320); fine=solve(640); finer=solve(1280)
    tolerance=solve(640, rtol=2e-10, atol=2e-12)
    first=float(np.max(np.linalg.norm(coarse-fine[:,::2],axis=2)))
    second=float(np.max(np.linalg.norm(fine-finer[:,::2],axis=2)))
    temporal=float(np.max(np.linalg.norm(fine-tolerance,axis=2)))
    if not second < first/3 or second > 3e-5 or temporal > 1e-6:
        raise ValueError('Refinement diagnostics failed')
    exported=fine[:,::4]
    frames=[{'t':round(float(t),3),'quarter':np.round(p,9).tolist()} for t,p in zip(TIMES,exported)]
    data={'name':'whitney-flow','kind':'whitney-flow','status':'numerical-pde',
          'description':'Exact initial Whitney profile; numerical n=2 equivariant flow for 0 <= t <= 0.09, before the singularity.',
          'intrinsicDimension':2,'ambientDimension':4,'normalization':'(dF/dt)^perp = Hvec (trace)',
          'snapshots':SNAPSHOTS,'frames':frames,
          'vertices':np.column_stack([profile(exported[0]),np.zeros(4*(len(exported[0])-1)+1)]).round(9).tolist(),
          'faces':[],'paths':[list(range(4*(len(exported[0])-1)+1))]}
    audit={'source':'Celso Viana, arXiv:1802.02108v2, (1.1), (2.2), Lemma 2.4, Theorem 1.3',
           'source_sha256':'992f374dc9b387fdc371dad9291f068fb5c4cb8ceb5e7e48b8391e2b5c756fd3',
           'equation':'gamma_t = gamma_uu / |gamma_u|^2 - gamma^perp / |gamma|^2; n=2; tangential diffusion gauge',
           'method':'Second-order centered differences, symmetry ghost points, method of lines with SciPy BDF',
           'quarter_intervals':[320,640,1280],'exported_quarter_intervals':160,
           'time_interval':[0,.09],'frame_spacing':.001,'rtol':2e-9,'atol':2e-11,'max_step':.0005,
           'max_pointwise_refinement_320_640':first,'max_pointwise_refinement_640_1280':second,
           'refinement_ratio':first/second,'max_pointwise_tolerance_change':temporal,
           'diagnostic_scope':'Mesh and tolerance comparisons, not certified error bounds or an extinction-time computation.',
           'singularity_included':False,'extinction_time':None,
           'final_tip_x':float(fine[-1,-1,0]),'final_max_y':float(fine[-1,:,1].max())}
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'whitney-flow.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'whitney-flow-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    (OUT/'whitney-flow.svg').write_text(svg(exported))
    print(json.dumps(audit,indent=2))

if __name__=='__main__':main()
