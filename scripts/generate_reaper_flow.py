"""Numerical finite-start CSF for Angenent--You's monotone three-reaper chain.

Regenerate with Python, NumPy and SciPy. This is a visualization, not a certified
approximation of the eternal limit. See documentation/grim-reaper-flow.md.
"""
from pathlib import Path
import argparse
import json
import numpy as np
from scipy.linalg import solve_banded
from scipy.interpolate import CubicSpline

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'site/assets/solitons'
TIMES = np.round(np.arange(-6, 9.0001, .1), 10)


def redistribute(points, count):
    s = np.r_[0., np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    targets = np.linspace(0, s[-1], count)
    return CubicSpline(s, points, axis=0)(targets)


def cutoff(x):
    u = np.clip((x + 1) / 2, 1e-10, 1-1e-10)
    a, b = np.exp(-1/u), np.exp(-1/(1-u))
    return a / (a + b)


def initial_curve(start=-10., extent=32., count=2401):
    # Eq. (3), a_k=k*pi, C_k=0: odd tips point right, even tips left.
    # Sample in angle near tips and in x along the nearly horizontal arms.
    t = start
    u = np.linspace(-extent, -t-.001, 5000)
    outer = np.column_stack([u, np.arcsin(np.exp(u+t))])
    y = np.linspace(outer[-1, 1], np.pi-np.arcsin(np.exp(1+t)), 5000)
    first = np.column_stack([np.log(np.sin(y))-t, y])
    x = np.linspace(1, -1, 1201)
    w = cutoff(x)
    y = w*(np.pi-np.arcsin(np.exp(x+t))) + (1-w)*(np.pi+np.arcsin(np.exp(t-x)))
    join = np.column_stack([x, y])
    y = np.linspace(join[-1, 1], 1.5*np.pi, 5000)
    middle = np.column_stack([-np.log(np.sin(y-np.pi))+t, y])
    lower = np.concatenate([outer, first[1:], join[1:], middle[1:]])
    upper = lower[-2::-1].copy()
    upper[:, 1] = 3*np.pi-upper[:, 1]
    return redistribute(np.concatenate([lower, upper]), count)


def evolve(points, start, times, dt=.002):
    """Backward Euler for X_t=X_ss, frozen arc metric, then redistribute.

    Tangential redistribution preserves the geometric normal velocity in the
    continuum limit. Both endpoints are held fixed outside the viewing window.
    """
    points = points.copy()
    n = len(points)
    t = start
    frames = []
    bands = np.zeros((3, n))
    for target in times:
        while t < target-1e-10:
            step = min(dt, target-t)
            lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
            left, right = lengths[:-1], lengths[1:]
            a = step*2/(left*(left+right))
            c = step*2/(right*(left+right))
            bands.fill(0)
            bands[1, :] = 1
            bands[1, 1:-1] += a+c
            bands[0, 2:] = -c
            bands[2, :-2] = -a
            points = redistribute(solve_banded((1, 1), bands, points), n)
            t += step
        frames.append(points.copy())
    return np.array(frames)


def run(count=2401, dt=.002, start=-10., extent=32., times=TIMES):
    return evolve(initial_curve(start, extent, count), start, times, dt)


def graph_distance(a, b):
    # x(y) comparisons on a fixed interior interval, away from truncated ends.
    y = np.linspace(.05, 3*np.pi-.05, 4001)
    return max(float(np.max(np.abs(np.interp(y, p[:,1], p[:,0])-np.interp(y, q[:,1], q[:,0])))) for p,q in zip(a,b))


def make_svg(data):
    # Six panels use exactly the same scale and window, including equal x/y units.
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="620" viewBox="0 0 960 620" role="img" aria-labelledby="title desc">',
           '<title id="title">Three-reaper chain under curve shortening at six times</title>',
           '<desc id="desc">Numerical finite-start evolution, with a fixed scale in all panels. One connected curve has three separated turns in the past and a broader profile later. The two outer ends continue to the left.</desc>',
           '<rect width="960" height="620" fill="#f7fafb"/>',
           '<g font-family="system-ui,sans-serif" fill="#183f52">',
           '<text x="30" y="32" font-size="21" font-weight="600">One curve, three alternating grim-reaper turns</text>',
           '<text x="30" y="56" font-size="13">Numerical curve-shortening evolution · aₖ = kπ, Cₖ = 0 · equal spatial scale in every panel</text>']
    for index,t in enumerate([-6,-3,0,3,6,9]):
        ox,oy = 22+(index%3)*312, 78+(index//3)*242
        out.append(f'<rect x="{ox}" y="{oy}" width="302" height="226" rx="5" fill="white" stroke="#d4e1e6"/>')
        out.append(f'<text x="{ox+14}" y="{oy+25}" font-size="17" font-weight="600">t = {t}</text>')
        scale=12.4
        sx=lambda x: ox+36+(x+12)*scale
        sy=lambda y: oy+182-y*scale
        out.append(f'<clipPath id="p{index}"><rect x="{sx(-12)}" y="{sy(3*np.pi)-4}" width="{20*scale}" height="{3*np.pi*scale+8}"/></clipPath>')
        for k in range(4):
            out.append(f'<path d="M {sx(-12):.2f} {sy(k*np.pi):.2f} H {sx(8):.2f}" fill="none" stroke="#b2c3cb" stroke-dasharray="4 4"/>')
            out.append(f'<text x="{ox+7}" y="{sy(k*np.pi)+4:.2f}" font-size="11">{["0","π","2π","3π"][k]}</text>')
        pts=data['frames'][round((t+6)*10)]['points']
        d=' '.join(('M' if i==0 else 'L')+f'{sx(x):.3f},{sy(y):.3f}' for i,(x,y) in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="#176b85" stroke-width="2.3" stroke-linejoin="round" clip-path="url(#p{index})"/>')
        out.append(f'<text x="{ox+14}" y="{oy+211}" font-size="11" fill="#526b77">x: −12 to 8 · outer ends continue left</text>')
    out.extend(['<text x="30" y="583" font-size="13">Finite-start approximation, not an exact formula or a certified eternal solution.</text>',
                '<text x="30" y="605" font-size="12">Angenent–You (2018), equation (3), §3.1–3.3 and Figure 9. Original numerical illustration.</text>', '</g></svg>'])
    (ASSETS/'grim-reaper-chains.svg').write_text('\n'.join(out)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', action='store_true')
    args=parser.parse_args()
    frames=run()
    # Arc-length resample for transport; preserve common indices for interpolation.
    small=[redistribute(p,901).round(6).tolist() for p in frames]
    data={'kind':'grim-reaper-flow','status':'numerical-pde','flat':True,
          'vertices':[[x,y,0] for x,y in small[0]],'faces':[], 'paths':[list(range(901))],
          'parameters':{'heights':[0,float(np.pi),float(2*np.pi),float(3*np.pi)],'shifts':[0,0,0], 'start':-10,'endpointsX':-32,'count':2401,'dt':.002},
          'window':[-12,8,0,float(3*np.pi)], 'frames':[{'t':float(t),'points':p} for t,p in zip(TIMES,small)]}
    (ASSETS/'grim-reaper-chains.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    make_svg(data)
    if args.audit:
        times=np.array([-6.,-3.,0.,3.,6.,9.])
        base=frames[[0,30,60,90,120,150]]
        fine=run(count=4801,dt=.001,times=times)
        earlier=run(start=-12.,times=times)
        wider=run(extent=40.,count=2801,times=times)
        q=np.linspace(-25,25,6000)
        y=2*np.arctan(np.exp(q))
        single=redistribute(np.column_stack([np.log(np.sin(y))+2,y]),1601)
        moved=evolve(single,-2.,[-1.],.002)[0]
        sample=np.linspace(.05,np.pi-.05,2000)
        benchmark=float(np.max(np.abs(np.interp(sample,moved[:,1],moved[:,0])-(np.log(np.sin(sample))+1))))
        audit={'single_reaper_translation_error':benchmark,'comparison':'max |x_A(y,t)-x_B(y,t)| for .05 <= y <= 3*pi-.05, at six displayed times; empirical, not a bound',
               'space_and_time_refinement':graph_distance(base,fine),
               'earlier_start':graph_distance(base,earlier),'farther_endpoints':graph_distance(base,wider),
               'minimum_y_increment':float(np.min(np.diff(frames[:,:,1],axis=1))),
               'signed_area_balance_error':float(np.trapezoid(base[-1,:,0],base[-1,:,1])-np.trapezoid(base[0,:,0],base[0,:,1])+15*np.pi),
               'reflection_symmetry_error':float(np.max(np.abs(frames[:,:,1]+frames[:,::-1,1]-3*np.pi))),
               'parameters':data['parameters']}
        (ASSETS/'grim-reaper-chains-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
        print(json.dumps(audit,indent=2))

if __name__=='__main__': main()
