"""Numerical illustration of Drugan's sphere (NumPy, SciPy, Matplotlib).

Source: Drugan, Trans. AMS 367 (2015), 3139--3159: equations (1.2)--(1.3),
Figure 1, Proposition 2.1, Section 5, and the power series in Section 6.
This shoots a numerical candidate for the reflection construction; it is
not a rigorous enclosure, an existence proof, or a uniqueness assertion.
"""
from pathlib import Path
import json
import math
import os

os.environ.setdefault('MPLCONFIGDIR', '/tmp/mcf-drugan-matplotlib')
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'


def rhs(s, y):
    r, z, theta = y
    return [math.cos(theta), math.sin(theta),
            (r/2 - 1/r)*math.sin(theta) - z/2*math.cos(theta)]


def shoot(b, eps=1e-4, rtol=2e-11, max_step=.025):
    # gamma(r)=b-b*r^2/8-b*(b^2+4)*r^4/1024+O(r^6).
    c = -b*(b*b+4)/1024
    initial = [eps, b-b*eps**2/8+c*eps**4,
               math.atan(-b*eps/4+4*c*eps**3)]
    def second_radial_turn(s, y):
        return y[2]+3*math.pi/2
    second_radial_turn.terminal = True
    second_radial_turn.direction = -1
    sol = solve_ivp(rhs, (0, 30), initial, method='DOP853', rtol=rtol,
                    atol=rtol/10, max_step=max_step, dense_output=True,
                    events=second_radial_turn)
    if not sol.success or not len(sol.t_events[0]):
        raise ValueError(f'No second radial turn for initial height {b}')
    return sol


def solve(**settings):
    b = brentq(lambda b: shoot(b, **settings).y[1, -1], .3, .5, xtol=5e-14)
    return b, shoot(b, **settings)


def profile(b, sol, count=121):
    half = sol.sol(np.linspace(0, sol.t[-1], count)).T
    # Include the analytic pole; omit the epsilon start from the coarse mesh.
    half[0] = [0, b, 0]
    # Record the unmodified residual in the audit before enforcing symmetry.
    half[-1, 1] = 0
    other = half[-2::-1].copy()
    other[:, 1] *= -1
    other[:, 2] = -3*math.pi-other[:, 2]
    return np.concatenate([half, other])


def mesh(p, segments=48):
    # One vertex at each pole, periodic angular rings, no degenerate triangles.
    vertices = [[0, 0, float(p[0, 1])]]
    rings = []
    for r, z, _ in p[1:-1]:
        ring = []
        for j in range(segments):
            angle = math.pi/2+2*math.pi*j/segments
            ring.append(len(vertices))
            vertices.append([r*math.cos(angle), r*math.sin(angle), z])
        rings.append(ring)
    south = len(vertices)
    vertices.append([0, 0, float(p[-1, 1])])
    faces, sectors, groups = [], [], []
    def add(face, j, group):
        faces.append(face); sectors.append(j); groups.append(group)
    for j in range(segments):
        k = (j+1) % segments
        add([0, rings[0][j], rings[0][k]], j, 0)
        for i in range(len(rings)-1):
            a, b = rings[i], rings[i+1]
            group = int(i+1 >= (len(p)-1)//2)
            add([a[j], b[j], b[k]], j, group)
            add([a[j], b[k], a[k]], j, group)
        add([rings[-1][j], south, rings[-1][k]], j, 1)
    return {'name': 'drugan-sphere', 'vertices': np.round(vertices, 7).tolist(),
            'faces': faces, 'paths': [], 'status': 'numerical-ode',
            'description': "Numerical Drugan immersed sphere in R3, Hvec=-Xperp/2; two reflected meridian halves.",
            'palette': [[67, 139, 169], [190, 120, 76]], 'faceGroups': groups,
            'view': {'pitch': .35},
            'revolution': {'segments': segments, 'faceSectors': sectors,
                           'degrees': 270, 'meridian': np.round(p[:, :2], 9).tolist()}}


def plot(p, data, audit):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    plt.rcParams.update({'svg.fonttype': 'none', 'svg.hashsalt': 'mcf-drugan', 'font.family': 'DejaVu Sans',
                         'font.size': 11, 'text.color': '#183f52',
                         'axes.labelcolor': '#183f52', 'axes.titlecolor': '#183f52'})
    fig = plt.figure(figsize=(11, 6), facecolor='#f7fafb')
    fig.suptitle("Drugan’s immersed shrinking sphere", fontsize=20, x=.06, ha='left', y=.95)
    fig.text(.06, .875, 'Numerical rotational ODE  •  '+r'$\mathbf{H}=-X^\perp/2$'+r'  •  $\Sigma\subset\mathbb{R}^3$', fontsize=12)
    ax = fig.add_axes([.075, .22, .38, .58], facecolor='#f7fafb')
    mid = len(p)//2
    for piece, color, label in [(p[:mid+1], '#21667f', 'Shot from the upper pole'),
                                (p[mid:], '#af673b', 'Reflected continuation')]:
        ax.plot(piece[:, 0], piece[:, 1], color=color, lw=2.4, label=label)
    ax.axvline(0, color='#869ca5', lw=.8)
    ax.axhline(0, color='#869ca5', lw=.8, ls='--')
    ax.scatter([0, 0], [p[0, 1], p[-1, 1]], color='#183f52', s=20, zorder=3)
    ax.scatter([p[mid, 0]], [0], color='#183f52', s=20, zorder=3)
    ax.set(xlabel=r'Radius $r$', ylabel=r'Height $z$', xlim=(-.25, 3.8), ylim=(-2, 2))
    ax.set_aspect('equal'); ax.spines[['top', 'right']].set_visible(False)
    ax.set_title('Generating meridian', fontsize=13, pad=12)
    ax.legend(loc='lower left', bbox_to_anchor=(.06, .115), bbox_transform=fig.transFigure,
              ncol=2, fontsize=9, frameon=False)
    ax3 = fig.add_axes([.48, .19, .49, .61], projection='3d', facecolor='#f7fafb')
    v = np.array(data['vertices'])
    faces = np.array(data['faces'])
    keep = np.array(data['revolution']['faceSectors']) < 36
    polys = v[faces[keep]]
    palette = np.array(data['palette'])/255
    colors = palette[np.array(data['faceGroups'])[keep]]
    poly = Poly3DCollection(polys, facecolors=colors, linewidths=0, antialiased=False, shade=True,
                            zsort='average')
    ax3.add_collection3d(poly)
    ax3.set(xlim=(-3.6, 3.6), ylim=(-3.6, 3.6), zlim=(-1.9, 1.9))
    ax3.set_box_aspect([7.2, 7.2, 3.8]); ax3.view_init(elev=22, azim=38)
    ax3.set_axis_off(); ax3.set_title('Surface of revolution · 270° cutaway', fontsize=13, pad=2)
    fig.text(.06, .08, f"Pole height b ≈ {audit['pole_height']:.8f}     Inner reflection radius ≈ {audit['reflection_radius']:.8f}", fontsize=11)
    fig.text(.06, .035, 'Cut edges are display boundaries. Numerical illustration; no certified error bounds or uniqueness claim.', fontsize=10, color='#526b77')
    fig.savefig(OUT/'drugan-sphere.svg', metadata={'Date': None, 'Description': data['description']})
    fig.savefig(OUT/'drugan-sphere.png', dpi=170)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    b, sol = solve()
    b_fine, fine = solve(eps=5e-5, rtol=2e-13, max_step=.0125)
    # Compare after accounting for the different omitted pole arc lengths.
    lo = 1e-3
    s = np.linspace(lo, sol.t[-1], 2001)
    shifted = fine.sol(s+5e-5)
    aligned_difference = np.max(np.abs(sol.sol(s)-shifted))
    max_r_s = brentq(lambda s: sol.sol(s)[2]+math.pi/2, 0, sol.t[-1])
    min_z_s = brentq(lambda s: sol.sol(s)[2]+math.pi, max_r_s, sol.t[-1])
    cross_s = brentq(lambda s: sol.sol(s)[1], 0, max_r_s)
    audit = {
        'source': 'Drugan (2015), equations (1.2)-(1.3), Figure 1, Sections 2-6',
        'normalization': 'Hvec=-Xperp/2', 'ambient_dimension': 3,
        'equations': "r'=cos(theta); z'=sin(theta); theta'=(r/2-1/r)sin(theta)-(z/2)cos(theta)",
        'pole_series': 'z=b-b*r^2/8-b*(b^2+4)*r^4/1024+O(r^6)',
        'shooting_bracket': [.3, .5],
        'bracket_endpoint_heights': [float(shoot(x).y[1, -1]) for x in [.3, .5]],
        'pole_height': b, 'reflection_radius': float(sol.y[0, -1]),
        'maximum_radius': float(sol.sol(max_r_s)[0]),
        'maximum_absolute_height': float(-sol.sol(min_z_s)[1]),
        'equatorial_crossing_radius': float(sol.sol(cross_s)[0]),
        'half_arc_length_from_epsilon': float(sol.t[-1]),
        'reflection_height_residual': float(abs(sol.y[1, -1])),
        'reflection_angle_residual': float(abs(sol.y[2, -1]+3*math.pi/2)),
        'settings': {'method': 'DOP853', 'epsilon': 1e-4, 'rtol': 2e-11, 'atol': 2e-12, 'max_step': .025},
        'refinement': {'epsilon': 5e-5, 'rtol': 2e-13, 'atol': 2e-14, 'max_step': .0125,
                       'pole_height_change': abs(b-b_fine),
                       'reflection_radius_change': float(abs(sol.y[0, -1]-fine.y[0, -1])),
                       'aligned_profile_max_component_change': float(aligned_difference)},
        'interpretation': 'Floating-point diagnostics before export rounding, not rigorous error bounds. Reflection and exact pole values close the display mesh. No claim that the numerical root uniquely identifies the supremum in Section 5.'}
    p = profile(b, sol)
    data = mesh(p)
    # Retain dense ODE samples for independent difference-quotient checks.
    data['shooting'] = {'arc': np.round(np.linspace(0, sol.t[-1], 801), 10).tolist(),
                        'states': np.round(sol.sol(np.linspace(0, sol.t[-1], 801)).T, 10).tolist()}
    (OUT/'drugan-sphere.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
    (OUT/'drugan-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    plot(profile(b, sol, 401), data, audit)
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
