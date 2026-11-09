"""Numerical rotational MCF from long convex seeds, not certified ancient slices.

Regeneration needs NumPy, SciPy and Pillow; the website uses committed data.
See documentation/hh-ancient-oval-picture.md for the equation and limitations.
"""
from pathlib import Path
import base64
import io
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from scipy.sparse import lil_matrix
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
TIMES = -10.0**np.linspace(3, -3, 121)


def evolve(length=8, intervals=512, tolerance=2e-9):
    """Support function in equatorial-radius units; outward normal angle theta."""
    theta = np.linspace(0, np.pi/2, intervals+1)
    step = theta[1]
    def geometry(h):
        extended = np.r_[h[1], h, h[-2]]
        first = (extended[2:]-extended[:-2])/(2*step)
        second = (extended[2:]-2*h+extended[:-2])/step**2
        meridian = h+second
        parallel = h+first*np.cos(theta)/np.maximum(np.sin(theta), 1e-20)
        parallel[0] = meridian[0]
        return 1/meridian+1/parallel, meridian, parallel
    def rhs(_, state):
        h = state[:-1]
        curvature = geometry(h)[0]
        return np.r_[-curvature+curvature[-1]*h, -curvature[-1]]
    sparsity = lil_matrix((intervals+2, intervals+2), dtype=int)
    for i in range(intervals+1):
        sparsity[i, max(0, i-1):min(intervals+1, i+2)] = 1
        sparsity[i, intervals-1:intervals+1] = 1
    sparsity[-1, intervals-1:intervals+1] = 1
    # Unit ball plus ellipsoid with semiaxes (length, 1/2, 1/2).
    h = 1+np.sqrt(length**2*np.cos(theta)**2+.25*np.sin(theta)**2)
    h /= h[-1]
    def round_enough(_, state):
        return state[0]-1.00000002
    round_enough.terminal = True
    round_enough.direction = -1
    solution = solve_ivp(rhs, [0, 100], np.r_[h, 0], method='BDF',
        rtol=tolerance, atol=tolerance/10, jac_sparsity=sparsity.tocsr(),
        max_step=.04, dense_output=True, events=round_enough)
    assert solution.success and len(solution.t_events[0]) == 1
    end = solution.t[-1]
    # S=(T-t)/b^2. Backward integration avoids subtracting nearly equal times.
    tail = solve_ivp(lambda s, y: 2*geometry(solution.sol(s)[:-1])[0][-1]*y-1,
        [end, 0], [.25], method='DOP853', rtol=2e-11, atol=2e-12,
        max_step=.04, dense_output=True)
    assert tail.success
    reference = brentq(lambda s: solution.sol(s)[0]-2, 0, end)
    def log_remaining(s):
        return 2*solution.sol(s)[-1]+np.log(tail.sol(s)[0])
    base = log_remaining(reference)
    frames = []
    minimum_radius = float('inf')
    sampled_support = []
    for time in TIMES:
        s = brentq(lambda v: log_remaining(v)-base-np.log(-time), 0, end)
        h = solution.sol(s)[:-1]
        H, rho1, rho2 = geometry(h)
        minimum_radius = min(minimum_radius, float(min(rho1.min(), rho2.min())))
        scale = 1/np.sqrt(tail.sol(s)[0])
        spline = CubicSpline(theta, h, bc_type=((1, 0), (1, 0)))
        derivative = spline(theta, 1)
        x = scale*(h*np.cos(theta)-derivative*np.sin(theta))
        r = scale*(h*np.sin(theta)+derivative*np.cos(theta))
        x[-1] = 0; r[0] = 0
        arc = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(r)))]
        samples = np.linspace(0, arc[-1], 65)
        quarter = np.column_stack([np.interp(samples, arc, x), np.interp(samples, arc, r)])
        profile = np.vstack([quarter, quarter[-2::-1]*[-1, 1]])
        frames.append(dict(time=float(time), aspect=float(h[0]),
            tip_curvature_rescaled=float(H[0]/scale),
            profile=np.round(profile, 7).tolist()))
        sampled_support.append(scale*spline(np.linspace(0, np.pi/2, 129)))
    return frames, np.array(sampled_support), dict(seed_length=length,
        seed_transverse_semiaxis=.5, intervals=intervals, tolerance=tolerance,
        minimum_rescaled_principal_radius=minimum_radius,
        terminal_aspect=float(solution.y[0,-1]),
        initial_normalized_time=-float(np.exp(log_remaining(0)-base)),
        normalized_sphere_rhs_error=float(np.abs(rhs(0, np.r_[np.ones(intervals+1), 0])[:-1]).max()))


def mesh(profile, segments=40):
    points = [[profile[0][0], 0, 0]]
    for x, r in profile[1:-1]:
        points.extend([[x, r*np.cos(a), r*np.sin(a)] for a in np.arange(segments)*2*np.pi/segments])
    pole = len(points); points.append([profile[-1][0], 0, 0])
    faces = []
    for j in range(segments):
        k = (j+1) % segments
        faces.append([0, 1+j, 1+k])
        for i in range(len(profile)-3):
            a=1+i*segments+j; b=1+i*segments+k
            faces.extend([[a, a+segments, b+segments], [a, b+segments, b]])
        a = 1+(len(profile)-3)*segments
        faces.append([a+j, pole, a+k])
    return np.array(points), np.array(faces)


def drawing(frames):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 700" role="img" aria-labelledby="title desc">',
        '<title id="title">An ancient oval through four times</title>',
        '<desc id="desc">Numerical rotational mean curvature flow from a long convex seed in three-space. Four surfaces at times minus 1000, minus 10, minus 1 and minus 0.001, all divided by square root of minus time and drawn at one common scale. Elongated shapes become round. Finite-seed computation, not certified ancient-flow data.</desc>',
        '<rect width="1100" height="700" fill="#f7fafb"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        '<text x="36" y="43" font-size="28" font-weight="600">Ancient oval · a flow through time</text>',
        '<text x="36" y="74" font-size="17">Surface case n = 2, j = 1 · numerical MCF from a long convex seed</text>',
        '<text x="36" y="102" font-size="17">Parabolic rescaling: every surface is divided by √(−t), at one common drawing scale.</text>']
    image = Image.new('RGBA', (2200, 1400)); painter = ImageDraw.Draw(image)
    for index, (frame_index, name) in enumerate([(0,'Elongated past'), (40,'Rounding'), (60,'Reference slice'), (120,'Near extinction')]):
        cx = 282+536*(index%2); cy = 232+238*(index//2)
        frame = frames[frame_index]; v, f = mesh(frame['profile'])
        yaw=.20; pitch=.27; x,y,z=v.T
        a=x*np.cos(yaw)-y*np.sin(yaw); b=x*np.sin(yaw)+y*np.cos(yaw)
        q=np.column_stack([a,z*np.cos(pitch)-b*np.sin(pitch),z*np.sin(pitch)+b*np.cos(pitch)])
        xy=np.column_stack([cx+42*q[:,0], cy-42*q[:,1]])
        for face in f[np.argsort(q[f,2].mean(axis=1))]:
            p0,p1,p2=q[face]; normal=np.cross(p1-p0,p2-p0); normal/=np.linalg.norm(normal)
            if normal[2]<0: normal=-normal
            light=.42+.57*max(0,normal @ [-.25,.55,.79])
            rgb=tuple(np.rint(np.array([66,143,167])*light).astype(int))+(255,)
            painter.polygon([(round(2*p[0]),round(2*p[1])) for p in xy[face]], fill=rgb)
        parts.extend([f'<text x="{cx-244}" y="{cy-98}" font-size="20" font-weight="600">t = {frame["time"]:g} · {name}</text>',
            f'<text x="{cx}" y="{cy+106}" text-anchor="middle" font-size="16">Length / width ≈ {frame["aspect"]:.2f}</text>'])
    buffer=io.BytesIO(); image.save(buffer,format='PNG',optimize=True)
    parts.append('<image width="1100" height="700" href="data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode()+'"/>')
    parts.extend(['<path d="M36 610H1064" stroke="#cbdce3"/>',
        '<text x="36" y="641" font-size="16">Original scale: all slices shrink to the origin as t → 0. Rescaled limit: a sphere of radius 2.</text>',
        '<text x="36" y="672" font-size="15">Haslhofer–Hershkovits, Theorem 1.1 and §3 · finite-seed approximation; no certified error to the ancient flow.</text>',
        '</g></svg>'])
    (OUT/'hh-ancient-ovals.svg').write_text('\n'.join(parts)+'\n')


def main():
    frames, support, audit = evolve()
    _, coarse, coarse_audit = evolve(intervals=256)
    _, shorter, shorter_audit = evolve(length=6)
    _, tighter, _ = evolve(tolerance=4e-10)
    audit.update(grid_refinement_max_support_difference=float(abs(support-coarse).max()),
        seed_length_max_support_difference=float(abs(support-shorter).max()),
        time_tolerance_max_support_difference=float(abs(support-tighter).max()),
        comparisons=[coarse_audit,shorter_audit],
        interpretation='Observed discretization and finite-seed comparisons, not rigorous error bounds to the ancient solution.')
    vertices, faces = mesh(frames[60]['profile'])
    epsilon=1e-5
    bowl=solve_ivp(lambda r,y: [y[1],(1+y[1]**2)*(1-y[1]/r)],
        [epsilon,4], [epsilon**2/4+epsilon**4/128,epsilon/2+epsilon**3/32],
        rtol=2e-11,atol=1e-12,dense_output=True)
    radii=np.linspace(epsilon,4,180)
    bowl_profile=np.vstack([[0,0],np.column_stack([-bowl.sol(radii)[0],radii])])
    data=dict(name='hh-ancient-ovals',kind='hh-numerical-flow',status='numerical-pde',
        vertices=np.round(vertices,7).tolist(),faces=faces.tolist(),paths=[],frames=frames,
        default_frame=60,snapshots=[0,40,60,120],segments=40,
        bowl_profile=np.round(bowl_profile,8).tolist(),
        normalization='Extinction at t=0; axial/equatorial radius ratio 2 at t=-1.',
        description='Finite-seed numerical rotational mean curvature flow, not a closed formula or certified ancient solution.',
        source='https://arxiv.org/abs/1308.4095v1',audit=audit)
    (OUT/'hh-ancient-ovals.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'hh-ancient-ovals-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    drawing(frames)
    print(json.dumps(audit,indent=2))

if __name__=='__main__':
    main()
