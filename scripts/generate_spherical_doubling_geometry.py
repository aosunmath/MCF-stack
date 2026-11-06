"""Spherical doubling construction schematic, NOT a solved self-shrinker.

NumPy/SciPy are needed only to regenerate the committed drawing assets.
See documentation/spherical-doubling-picture.md for sources and limitations.
"""
from collections import defaultdict, deque
from pathlib import Path
import base64
import io
import json
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
COUNTS = [6, 10, 14]
COLORS = np.array([[75, 139, 163], [211, 169, 99], [188, 116, 77]])


def balanced_latitude(end=15, tol=1e-11):
    """Numerical RLD guide from (7.20), (7.25), (7.29), (10.3)."""
    def rhs(s, y):
        return [y[1], -4 / np.cosh(s)**2 * y[0]]
    even = solve_ivp(rhs, [0, 2], [1, 0], rtol=tol, atol=tol/10, dense_output=True)
    pole = solve_ivp(rhs, [end, 0], [1, 0], rtol=tol, atol=tol/10, dense_output=True)
    a = brentq(lambda s: pole.sol(s)[0], 0, 1.5)
    b = brentq(lambda s: even.sol(s)[0], 0, 1.5)
    def balance(s):
        e, p = even.sol(s), pole.sol(s)
        return e[1]/e[0] + p[1]/p[0]
    s = brentq(balance, a+1e-5, b-1e-5, xtol=1e-14)
    return s, float(abs(balance(s)))


def orient_and_audit(vertices, faces):
    """Orient one connected closed mesh; reject nonmanifold seams."""
    edges = defaultdict(list)
    for j, f in enumerate(faces):
        for a, b in zip(f, np.roll(f, -1)):
            edges[tuple(sorted((a, b)))].append((j, 1 if a < b else -1))
    assert all(len(v) == 2 for v in edges.values())
    neighbors = defaultdict(list)
    for pair in edges.values():
        (i, a), (j, b) = pair
        neighbors[i].append((j, -a*b)); neighbors[j].append((i, -a*b))
    signs = {0: 1}; queue = deque([0])
    while queue:
        i = queue.popleft()
        for j, relation in neighbors[i]:
            value = signs[i]*relation
            if j in signs:
                assert signs[j] == value
            else:
                signs[j] = value; queue.append(j)
    assert len(signs) == len(faces)
    faces = np.array([f if signs[i] == 1 else f[::-1] for i, f in enumerate(faces)])
    a, b, c = vertices[faces].transpose(1, 0, 2)
    volume = np.sum(a*np.cross(b, c))/6
    if volume < 0:
        faces = faces[:, ::-1]
    normals = np.zeros_like(vertices)
    a, b, c = vertices[faces].transpose(1, 0, 2)
    cross = np.cross(b-a, c-a)
    for i in range(3):
        np.add.at(normals, faces[:, i], cross)
    norms = np.linalg.norm(normals, axis=1)
    assert np.min(norms) > 1e-10
    normals /= norms[:, None]
    chi = len(vertices)-len(edges)+len(faces)
    return faces, normals, dict(vertices=len(vertices), faces=len(faces),
        components=1, boundary_edges=0, edge_incidence=[2], orientable=True,
        euler_characteristic=chi, genus=(2-chi)//2,
        minimum_triangle_area=float(np.linalg.norm(cross, axis=1).min()/2))


def make_mesh(m, s, samples=5200, segments=36, rings=28):
    z = math.tanh(s); rho = math.sqrt(1-z*z)
    sites = np.array([[rho*math.cos(2*math.pi*j/m), rho*math.sin(2*math.pi*j/m), sign*z]
                      for sign in [-1, 1] for j in range(m)])
    # Geodesic patch radius b, waist tau, and sheet separation are drawing choices.
    b = min(.40, 1.5*rho*math.sin(math.pi/m))
    tau = .22*b; half_gap = tau*math.acosh(b/tau)
    theta = np.linspace(0, 2*np.pi, segments, endpoint=False)
    def directions(n, t):
        e1 = np.cross([0, 0, 1], n); e1 /= np.linalg.norm(e1)
        e2 = np.cross(n, e1)
        tangent = np.cos(theta)[:, None]*e1 + np.sin(theta)[:, None]*e2
        return math.cos(t/2)*n + math.sin(t/2)*tangent
    # Spherical triangulation with explicitly shared circular hole boundaries.
    k = np.arange(samples); zz = 1-2*(k+.5)/samples
    aa = k*math.pi*(3-math.sqrt(5))
    q = np.column_stack([np.sqrt(1-zz*zz)*np.cos(aa), np.sqrt(1-zz*zz)*np.sin(aa), zz])
    q = q[np.max(q @ sites.T, axis=1) < math.cos(b/2+.018)]
    boundaries = []
    for n in sites:
        boundaries.append(np.arange(len(q), len(q)+segments))
        q = np.vstack([q, directions(n, b)])
    hull = ConvexHull(q)
    faces = hull.simplices
    centers = q[faces].mean(axis=1)
    faces = faces[np.max(centers @ sites.T, axis=1) < math.cos(b/2)-1e-10]
    nq = len(q)
    vertices = np.vstack([(2+half_gap)*q, (2-half_gap)*q]).tolist()
    result = np.vstack([faces, faces+nq]).tolist()
    groups = [0]*len(faces) + [1]*len(faces)
    vertex_groups = [0]*nq + [1]*nq
    umax = math.acosh(b/tau)
    for n, boundary in zip(sites, boundaries):
        loops = [boundary+nq]
        for u in np.linspace(-umax, umax, rings+1)[1:-1]:
            t = tau*math.cosh(u)
            w = np.clip((t-.6*b)/(.4*b), 0, 1)
            blend = w**3*(10-15*w+6*w*w)
            h = (1-blend)*tau*abs(u)+blend*half_gap
            p = (2+math.copysign(h, u))*directions(n, t)
            loops.append(np.arange(len(vertices), len(vertices)+segments))
            vertices.extend(p.tolist()); vertex_groups.extend([2]*segments)
        loops.append(boundary)
        for lower, upper in zip(loops, loops[1:]):
            for i in range(segments):
                j = (i+1) % segments
                result.extend([[lower[i], lower[j], upper[j]], [lower[i], upper[j], upper[i]]])
                groups.extend([2, 2])
    vertices = np.array(vertices)
    faces, normals, audit = orient_and_audit(vertices, np.array(result))
    assert audit['genus'] == 2*m-1, audit
    assert len(vertices) < 65536
    # Caps are disjoint and radial coordinates positive throughout the display slider.
    distances = np.arccos(np.clip(sites @ sites.T, -1, 1)) + np.eye(2*m)*10
    audit.update(bridge_count=2*m, patch_radius=b, waist_radius=tau,
                 half_gap=half_gap, minimum_site_angle=float(distances.min()))
    assert distances.min() > b  # Two patch radii b/2 on the unit sphere.
    data = dict(name='sphere-doubling-shrinker', kind='spherical-doubling-schematic',
        status='schematic', m=m, genus=2*m-1, counts=COUNTS,
        vertices=np.round(vertices, 7).tolist(), normals=np.round(normals, 7).tolist(),
        faces=faces.tolist(), paths=[], faceGroups=groups, vertexGroups=vertex_groups,
        palette=COLORS.tolist(), sites=np.round(2*sites, 9).tolist(),
        view=dict(yaw=.23, pitch=.27, radius=2.5),
        construction=dict(base_radius=2, balanced_s=s, patch_radius=b, waist_radius=tau,
                          half_gap=half_gap, segments=segments, rings=rings),
        description='Two nearby spherical sheets joined through catenoidal neck charts. '
        'Original construction schematic; not a computed self-shrinker or a certified approximation.')
    return data, audit


def drawing(data):
    """Printable plate: rendered mesh views with vector labels and neck section."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 790" role="img" aria-labelledby="title desc">',
        '<title id="title">Spherical doubling: two sheets joined through radial necks</title>',
        '<desc id="desc">Original construction schematic informed by Kapouleas and McGrath. '
        'Full surface and cutaway show two spherical sheets connected through twenty radial necks '
        'on two aligned latitude circles. A local section explains the catenoidal connection. '
        'Model genus nineteen; no small-genus existence claim. Not a solved self-shrinker.</desc>',
        '<rect width="1100" height="790" fill="#f7fafb"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        '<text x="38" y="46" font-size="28" font-weight="600">Spherical doubling</text>',
        '<text x="38" y="78" font-size="18" fill="#58727e">Two nearby spherical sheets, connected through radial catenoidal necks</text>']
    vertices = np.array(data['vertices']); faces = np.array(data['faces'])
    # Supersampled raster geometry keeps the self-contained SVG small and avoids
    # antialias cracks between thousands of adjacent vector triangles.
    surface = Image.new('RGBA', (3300, 2370))
    painter = ImageDraw.Draw(surface)
    yaw, pitch = .23, .27
    x, y, z = vertices.T
    a=x*np.cos(yaw)-y*np.sin(yaw); b=x*np.sin(yaw)+y*np.cos(yaw)
    q=np.column_stack([a, z*np.cos(pitch)-b*np.sin(pitch), z*np.sin(pitch)+b*np.cos(pitch)])
    for cx, cut in [(276, False), (824, True)]:
        xy=np.column_stack([cx+85*q[:, 0], 300-85*q[:, 1]])
        for j in np.argsort(q[faces, 2].mean(axis=1)):
            f=faces[j]; a,b,c=q[f]; n=np.cross(b-a,c-a); n/=np.linalg.norm(n)
            if n[2]<0: n=-n
            light=.48+.50*max(0, n @ np.array([-.35,.55,.76]))
            rgb=np.rint(COLORS[data['faceGroups'][j]]*light).astype(int)
            polygon=list(xy[f])
            if cut:
                polygon=[]
                for ia,ib in zip(f,np.roll(f,-1)):
                    ya,yb=vertices[ia,1],vertices[ib,1]
                    if ya<=0: polygon.append(xy[ia])
                    if (ya<=0)!=(yb<=0): polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(polygon)<3: continue
            painter.polygon([(round(3*p[0]), round(3*p[1])) for p in polygon],
                            fill=tuple(int(v) for v in rgb)+(255,))
        parts.append(f'<text x="{cx}" y="510" text-anchor="middle" font-size="19" font-weight="600">'
                     f'{"Front half removed to expose the inner sheet" if cut else "One closed, connected surface"}</text>')
    buffer = io.BytesIO()
    surface.resize((2200,1580), Image.Resampling.LANCZOS).save(buffer, format='PNG', optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    parts.append(f'<image width="1100" height="790" href="data:image/png;base64,{encoded}"/>')
    parts += ['<path d="M38 540H1062" stroke="#cedde3"/>',
        '<circle cx="48" cy="568" r="6" fill="#4b8ba3"/><text x="64" y="574" font-size="17">Outer sheet</text>',
        '<circle cx="237" cy="568" r="6" fill="#d3a963"/><text x="253" y="574" font-size="17">Inner sheet</text>',
        '<circle cx="424" cy="568" r="6" fill="#bc744d"/><text x="440" y="574" font-size="17">Connecting necks</text>',
        '<text x="38" y="615" font-size="17">m = 10 sites per latitude · 20 bridges · model genus 2m − 1 = 19</text>',
        '<text x="38" y="644" font-size="17">Balanced linearized latitude guide; neck size and gap enlarged.</text>',
        '<text x="38" y="673" font-size="17">Existence requires sufficiently large m; the displayed values are illustrative.</text>',
        '<text x="826" y="572" text-anchor="middle" font-size="16" font-weight="600">Local neck section</text>',
        '<path d="M710 604H775 M877 604H942" stroke="#4b8ba3" stroke-width="3"/>',
        '<path d="M710 672H775 M877 672H942" stroke="#d3a963" stroke-width="3"/>',
        '<path d="M775 604C830 604 830 672 775 672 M877 604C822 604 822 672 877 672" fill="none" stroke="#bc744d" stroke-width="3"/>',
        '<text x="826" y="701" text-anchor="middle" font-size="14" fill="#58727e">The sheets join around an open throat.</text>',
        '<path d="M38 722H1062" stroke="#cedde3"/>',
        '<text x="38" y="755" font-size="17" font-weight="600">CONSTRUCTION SCHEMATIC · not a solved self-shrinker · cut edges belong only to the display</text>',
        '</g></svg>']
    (OUT/'sphere-doubling-shrinker.svg').write_text('\n'.join(parts)+'\n')


def main():
    s, residual = balanced_latitude()
    refined, _ = balanced_latitude(18, 1e-12)
    audits = {}
    for m in COUNTS:
        data, audits[str(m)] = make_mesh(m, s)
        name = 'sphere-doubling-shrinker' if m == 10 else f'sphere-doubling-shrinker-{m}'
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
        if m == 10:
            drawing(data)
    audit = dict(status='schematic', source='https://arxiv.org/pdf/2001.04240v4',
        source_locations='Theorem A; Definitions 7.10–7.11, 7.29; equation (10.3); Theorem 10.5',
        balanced_s=s, latitude_degrees=math.degrees(math.asin(math.tanh(s))),
        flux_balance_residual=residual, refined_latitude_s_change=abs(refined-s), models=audits)
    (OUT/'sphere-doubling-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
