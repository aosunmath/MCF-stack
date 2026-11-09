"""Annulus-dense shrinkers: Halldorsson (2012), Sections 2 and 5.

Numerical one-period profiles; exact similarity law and rotated continuation.
Run with Python + NumPy/SciPy. No source paper is redistributed.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
TIMES = [-4, -1, -.25, -.0625]


def rhs(s, y):
    u, v, theta = y
    return [u*v, .5-u*u, u]


def excursion(r, tol=2e-12, samples=801):
    # From an inner contact, the first downward v=0 crossing is the outer
    # contact. Reflection of the phase orbit gives the full period.
    def outer(s, y):
        return y[1]
    outer.direction = -1
    outer.terminal = True
    half = solve_ivp(rhs, [0, 30], [r/2, 0, 0], method='DOP853',
                     rtol=tol, atol=tol/20, events=outer, max_step=.025)
    if not half.success or len(half.t_events[0]) != 1:
        raise ValueError('Outer contact was not found')
    period = 2*half.t_events[0][0]
    sol = solve_ivp(rhs, [0, period], [r/2, 0, 0], method='DOP853',
                    rtol=tol, atol=tol/20, dense_output=True, max_step=.025)
    if not sol.success:
        raise ValueError(sol.message)
    y = sol.sol(np.linspace(0, period, samples))
    z = -2j*np.exp(1j*y[2])*(y[0]+1j*y[1])
    return period, y, z


def rotated_points(base, alpha, count):
    return np.concatenate([base[:-1]*np.exp(2j*np.pi*alpha*j) for j in range(count)]
                          + [base[-1:]*np.exp(2j*np.pi*alpha*(count-1))])


def profile(name, target, expression):
    r = brentq(lambda x: excursion(x, samples=2)[1][2, -1]/(2*np.pi)-target,
               .03, 1.35, xtol=5e-14)
    period, y, z = excursion(r)
    alpha = float(y[2, -1]/(2*np.pi))
    _, yr, zr = excursion(r, tol=8e-14)
    rmax = float(abs(z[len(z)//2]))
    tiled = rotated_points(z, alpha, 12)
    # Independent integration across all twelve periods tests continuation,
    # including the joins. Neither seam is artificially closed.
    direct = solve_ivp(rhs, [0, 12*period], [r/2, 0, 0], method='DOP853',
                       rtol=8e-14, atol=4e-15, max_step=.02,
                       t_eval=np.linspace(0, 12*period, len(tiled)))
    yd = direct.y
    zd = -2j*np.exp(1j*yd[2])*(yd[0]+1j*yd[1])
    invariant = y[0]*np.exp(-abs(z)**2/4)
    audit = dict(turning_residual=float(alpha-target),
                 phase_return=float(np.linalg.norm(y[:2, -1]-y[:2, 0])),
                 invariant_drift=float(np.ptp(invariant)),
                 refinement_max=float(np.max(abs(z-zr))),
                 continuation_max=float(np.max(abs(tiled-zd))),
                 radius_relation_residual=float(abs(r*np.exp(-r*r/4)-rmax*np.exp(-rmax*rmax/4))))
    vertices = np.column_stack([tiled.real, tiled.imag, np.zeros(len(tiled))]).round(10).tolist()
    return dict(name=name, target_expression=expression, target=float(target), alpha=alpha,
                r_min=float(r), r_max=rmax, period=float(period), A=0, B=-.5,
                base=np.column_stack([z.real, z.imag]).round(12).tolist(),
                curvature=y[0].round(12).tolist(), theta=y[2].round(12).tolist(),
                vertices=vertices, paths=[list(range(len(vertices)))], faces=[],
                window=[0, 12*float(period)],
                note='Finite numerical profile. Irrational turning is prescribed mathematically; floating-point shooting does not certify it.',
                diagnostics=audit)


def drawing(data):
    v = data['variants'][0]
    base = np.array(v['base']); z = base[:, 0]+1j*base[:, 1]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 730" role="img" aria-labelledby="title desc">',
           '<title id="title">An annulus-dense curve and its shrinking flow</title>',
           '<desc id="desc">Twelve and ninety-six excursions of a numerical nonclosed shrinker. Four time slices use the same spatial scale. Orange highlights the same excursion; dashed circles mark the image closure, not additional flow components.</desc>',
           '<rect width="960" height="730" rx="12" fill="#f6f9fa"/>',
           '<g font-family="system-ui,sans-serif" fill="#203e4a">',
           '<text x="30" y="39" font-size="25" font-weight="600">One curve, repeated excursions</text>',
           '<text x="30" y="70" font-size="19">Numerical ODE · α = 1/√2 − 1/100 ≈ 0.697107 · t = −1</text>']

    def panel(cx, cy, scale, count, time):
        g = np.sqrt(-time)
        for radius in [v['r_min'], v['r_max']]:
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{radius*g*scale:.3f}" fill="none" stroke="#7b8790" stroke-dasharray="5 5" stroke-width="1.3"/>')
        for j in range(count):
            zz = z*np.exp(2j*np.pi*v['alpha']*j)*g
            pts = ' '.join(f'{cx+p.real*scale:.2f},{cy-p.imag*scale:.2f}' for p in zz[::2])
            out.append(f'<polyline points="{pts}" fill="none" stroke="#216c83" stroke-opacity="{.65 if count<20 else .35}" stroke-width="{1.2 if count<20 else .8}"/>')
        pts = ' '.join(f'{cx+p.real*g*scale:.2f},{cy-p.imag*g*scale:.2f}' for p in z[::2])
        out.append(f'<polyline points="{pts}" fill="none" stroke="#c45b32" stroke-width="3"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="#52636d"/>')

    for cx, count in [(240, 12), (720, 96)]:
        panel(cx, 250, 138/v['r_max'], count, -1)
        out.append(f'<text x="{cx}" y="418" text-anchor="middle" font-size="21">{count} excursions · finite window</text>')
    out.extend(['<path d="M30 443H930" stroke="#d1dde2"/>',
                '<text x="30" y="478" font-size="24" font-weight="600">The same segment at four times</text>',
                '<text x="30" y="509" font-size="19">X(s,t) = √(−t) X(s) · same spatial scale in every panel</text>'])
    for cx, time, label, factor in zip([130, 365, 600, 835], TIMES, ['−4', '−1', '−1/4', '−1/16'], ['2', '1', '1/2', '1/4']):
        panel(cx, 604, 72/(2*v['r_max']), 12, time)
        out.append(f'<text x="{cx}" y="700" text-anchor="middle" font-size="20">t = {label} · scale {factor}</text>')
    out.append('</g></svg>\n')
    (OUT/'halldorsson-dense.svg').write_text(''.join(out))


def generate():
    variants = [profile('Narrow annulus', 1/np.sqrt(2)-.01, '1/√2 − 1/100'),
                profile('Broad annulus', (np.sqrt(5)-1)/2, '(√5 − 1)/2')]
    data = dict(title='Nonclosed annulus-dense shrinker', dimension=2, motion='similarity',
                snapshot_times=TIMES, variants=variants)
    (OUT/'halldorsson-dense.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
    audit = dict(source='Halldorsson, arXiv:1007.1617v2, §2 and §5, Theorem 5.1, pp. 11–13; Figures 4–7, pp. 17–18.',
                 normalization='A=0, B=-1/2; time -1 profile; X(s,t)=sqrt(-t)X(s), t<0.',
                 method='DOP853 shooting to an irrational target; one complete phase period, then rotated continuation. 801 samples per excursion.',
                 limitations='Floating-point diagnostics, not certified error bounds or a numerical proof of irrationality. Only finite parameter windows are drawn.',
                 profiles=[{k:v[k] for k in ['name', 'target_expression', 'alpha', 'r_min', 'r_max', 'period', 'diagnostics']} for v in variants])
    (OUT/'annulus-shrinker-audit.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False)+'\n')
    drawing(data)
    template = (ROOT/'scripts/templates/annulus-shrinker.html').read_text()
    page = template.replace('<!-- GEOMETRY -->', json.dumps(data, separators=(',', ':')))
    page = page.replace('/* VIEWER */', (ROOT/'site/assets/annulus-shrinker-viewer.mjs').read_text())
    (ROOT/'site/experiments/halldorsson-dense.html').write_text(page)
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    generate()
