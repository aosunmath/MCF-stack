"""Original Shao–Zou construction schematic, NOT a computed self-shrinker.

Requires NumPy, SciPy and Pillow only for regeneration. See
documentation/shao-zou-picture.md for the source ledger and drawing choices.
"""
from collections import defaultdict, deque
from pathlib import Path
import base64
import io
import json
import math

import numpy as np
from scipy.optimize import brentq
from scipy.spatial import Delaunay
from scipy.special import hyp1f1, hyperu
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
LAYERS = [2, 3, 4, 5, 6]
COUNTS = [6, 10, 14]
RIM = 3.2
COLORS = np.array([[71, 129, 158], [101, 163, 169], [171, 188, 165],
                   [218, 181, 116], [224, 157, 107], [201, 128, 94], [174, 99, 68]])


def balanced_radius():
    """Equation (3.12), not the solved finite-m neck locations."""
    def balance(r):
        x = r*r/4
        return (-r*hyp1f1(.5, 2, x)/(4*hyp1f1(-.5, 1, x))
                + r*hyperu(.5, 2, x)/(4*hyperu(-.5, 1, x)) - r/2)
    radius = brentq(balance, 1, 2, xtol=1e-14)
    return radius, abs(balance(radius))


def profile(r, radius):
    """Normalized RLD radial branches (4.12), with an illustrative smooth collar."""
    r = np.asarray(r)
    inner = hyp1f1(-.5, 1, np.minimum(r, radius+.2)**2/4)/hyp1f1(-.5, 1, radius**2/4)
    outer = hyperu(-.5, 1, np.maximum(r, radius-.2)**2/4)/hyperu(-.5, 1, radius**2/4)
    t = np.clip((r-radius+.16)/.32, 0, 1)
    w = t*t*t*(10-15*t+6*t*t)
    return inner*(1-w)+outer*w


def audit_mesh(vertices, faces, k, m):
    edges = defaultdict(list)
    for i, f in enumerate(faces):
        for a, b in zip(f, np.roll(f, -1)):
            edges[tuple(sorted((a, b)))].append((i, 1 if a < b else -1))
    assert {len(v) for v in edges.values()} == {1, 2}
    neighbors = defaultdict(list)
    boundary = defaultdict(set)
    for (a, b), pair in edges.items():
        if len(pair) == 1:
            boundary[a].add(b); boundary[b].add(a)
        else:
            (i, x), (j, y) = pair
            neighbors[i].append((j, -x*y)); neighbors[j].append((i, -x*y))
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
    assert all(len(v) == 2 for v in boundary.values())
    unseen = set(boundary); loops = 0
    while unseen:
        loops += 1; queue = [unseen.pop()]
        while queue:
            for j in boundary[queue.pop()]:
                if j in unseen:
                    unseen.remove(j); queue.append(j)
    assert loops == k
    assert np.max(np.abs(np.linalg.norm(vertices[list(boundary), :2], axis=1)-RIM)) < 1e-8
    chi = len(vertices)-len(edges)+len(faces)
    genus = (2-loops-chi)//2
    assert genus == (k-1)*(m-1)
    a, b, c = vertices[faces].transpose(1, 0, 2)
    cross = np.cross(b-a, c-a)
    assert np.linalg.norm(cross, axis=1).min() > 1e-10
    normals = np.zeros_like(vertices)
    for i in range(3):
        np.add.at(normals, faces[:, i], cross)
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    return faces, normals, dict(vertices=len(vertices), faces=len(faces), components=1,
        boundary_loops=loops, genus=genus, euler_characteristic=chi,
        orientable=True, bridges=(k-1)*m, minimum_triangle_area=float(np.linalg.norm(cross, axis=1).min()/2))


def make_mesh(k, m, radius, segments=24, rings=16):
    # All neck patches, including staggered patches on intermediate sheets,
    # are disjoint. Widths and heights are enlarged for visibility.
    patch = .72*radius*math.sin(math.pi/(2*m))
    waist = .25*patch
    amplitude = .48*k*patch
    levels = -amplitude*np.cos(math.pi*(np.arange(k)+.5)/k)
    sites = [np.array([[radius*math.cos(2*math.pi*j/m+(gap%2)*math.pi/m),
                       radius*math.sin(2*math.pi*j/m+(gap%2)*math.pi/m)]
                      for j in range(m)]) for gap in range(k-1)]
    vertices, faces, groups, boundaries = [], [], [], {}
    angles = np.arange(segments)*2*math.pi/segments
    local = np.column_stack([np.cos(angles), np.sin(angles)])
    # Symmetric point samples with explicit circular hole boundaries. Every
    # collar shares its vertex indices with the sheets: no overlay cylinders.
    base = [[0., 0.]]
    for r in np.linspace(.10, RIM, 37):
        count = max(2*m, 2*m*math.ceil(2*math.pi*r/(2*m*.15)))
        theta = np.arange(count)*2*math.pi/count
        base.extend(np.column_stack([r*np.cos(theta), r*np.sin(theta)]))
    base = np.array(base)
    for layer in range(k):
        gaps = [g for g in [layer-1, layer] if 0 <= g < k-1]
        centers = np.concatenate([sites[g] for g in gaps])
        distance = np.linalg.norm(base[:, None, :]-centers[None, :, :], axis=2).min(axis=1)
        points = base[distance > patch+.025]
        offset = len(vertices)
        for gap in gaps:
            for j, site in enumerate(sites[gap]):
                boundaries[layer, gap, j] = np.arange(len(points), len(points)+segments)+offset
                # Rotate local samples with the site to retain discrete symmetry.
                theta = math.atan2(site[1], site[0])
                rotation = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
                points = np.vstack([points, site+patch*(local @ rotation.T)])
        triangles = Delaunay(points).simplices
        centroids = points[triangles].mean(axis=1)
        distances = np.linalg.norm(centroids[:, None, :]-centers[None, :, :], axis=2).min(axis=1)
        triangles = triangles[distances > patch*math.cos(math.pi/segments)]
        z = levels[layer]*profile(np.linalg.norm(points, axis=1), radius)
        vertices.extend(np.column_stack([points, z]).tolist())
        faces.extend((triangles+offset).tolist()); groups.extend([layer]*len(points))
    umax = math.acosh(patch/waist)
    for gap in range(k-1):
        for j, site in enumerate(sites[gap]):
            theta = math.atan2(site[1], site[0])
            rotation = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
            circle = local @ rotation.T
            loops = [boundaries[gap, gap, j]]
            for u in np.linspace(-umax, umax, rings+1)[1:-1]:
                rho = waist*math.cosh(u)
                p = site+rho*circle
                # Flatten the last collar onto the curved sheet; the central
                # throat retains the cosh profile, with illustrative z scaling.
                t = abs(u)/umax
                w = np.clip((t-.65)/.35, 0, 1)
                w = w*w*w*(10-15*w+6*w*w)
                h = math.copysign((1-w)*t+w, u)
                coefficient = (levels[gap+1]+levels[gap])/2+h*(levels[gap+1]-levels[gap])/2
                z = coefficient*profile(np.linalg.norm(p, axis=1), radius)
                loops.append(np.arange(len(vertices), len(vertices)+segments))
                vertices.extend(np.column_stack([p, z]).tolist()); groups.extend([6]*segments)
            loops.append(boundaries[gap+1, gap, j])
            for lower, upper in zip(loops, loops[1:]):
                for a in range(segments):
                    b = (a+1)%segments
                    faces.extend([[lower[a], lower[b], upper[b]], [lower[a], upper[b], upper[a]]])
    vertices = np.array(vertices)
    faces, normals, audit = audit_mesh(vertices, np.array(faces), k, m)
    assert len(vertices) < 65536
    data = dict(name='shao-zou-stacking', kind='shao-zou-schematic', status='schematic',
        k=k, m=m, genus=(k-1)*(m-1), vertices=np.round(vertices, 6).tolist(),
        faces=faces.tolist(), paths=[], vertexGroups=groups, palette=COLORS.tolist(),
        view=dict(yaw=.18, pitch=.30, radius=RIM, gap=1.35),
        construction=dict(balanced_radius=radius, patch_radius=patch, waist_radius=waist,
            levels=levels.tolist(), sites=[p.tolist() for p in sites], segments=segments,
            rings=rings, display_radius=RIM),
        description='Original connected construction schematic with staggered open necks. '
        'RLD-inspired sheet profiles; illustrative gaps, neck sizes and end slopes. '
        'Not a solved self-shrinker or a certified approximation.')
    return data, audit


def drawing(data):
    """Original static plate, with geometry and separate placement diagram."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 760" role="img" aria-labelledby="title desc">',
        '<title id="title">Shao–Zou: staggered bridges between four sheets</title>',
        '<desc id="desc">Construction schematic with four truncated ends, ten bridges per adjacent pair and genus twenty-seven. A cutaway exposes open necks. The plan diagram shows the half-step offset between consecutive bridge rings. Not a solved self-shrinker.</desc>',
        '<rect width="1100" height="760" fill="#f7fafb"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        '<text x="34" y="44" font-size="27" font-weight="600">Shao–Zou: staggered bridges between sheets</text>',
        '<text x="34" y="76" font-size="18" fill="#58727e">Four ends · ten necks per gap · thirty bridges · model genus 27</text>']
    vertices = np.array(data['vertices']); vertices[:, 2] *= data['view']['gap']
    faces = np.array(data['faces']); palette = COLORS[np.array(data['vertexGroups'])]
    canvas = Image.new('RGBA', (3300, 2280)); painter = ImageDraw.Draw(canvas)
    yaw, pitch = .18, .30
    cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    q = vertices @ np.array([[cy,-sy,0],[-sy*sp,-cy*sp,cp],[sy*cp,cy*cp,sp]]).T
    for cx, cut in [(275, False), (825, True)]:
        xy = np.column_stack([cx+68*q[:, 0], 250-68*q[:, 1]])
        for i in np.argsort(q[faces, 2].mean(axis=1)):
            f = faces[i]; a,b,c = q[f]; n = np.cross(b-a,c-a); n /= np.linalg.norm(n)
            if n[2]<0: n=-n
            light = .52+.47*max(0, n @ np.array([-.35,.55,.76]))
            rgb = np.rint(palette[f].mean(axis=0)*light).astype(int)
            polygon = list(xy[f])
            if cut:
                polygon = []
                for ia,ib in zip(f,np.roll(f,-1)):
                    ya,yb=vertices[ia,1],vertices[ib,1]
                    if ya<=0: polygon.append(xy[ia])
                    if (ya<=0)!=(yb<=0): polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(polygon)<3: continue
            painter.polygon([(round(3*p[0]),round(3*p[1])) for p in polygon], fill=tuple(rgb)+(255,))
    buffer = io.BytesIO()
    canvas.resize((2200,1520), Image.Resampling.LANCZOS).save(buffer, format='PNG', optimize=True)
    parts.append(f'<image width="1100" height="760" href="data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"/>')
    for cx,label in [(275,'Full surface'),(825,'Front half removed: look into the gaps')]:
        parts.append(f'<text x="{cx}" y="430" text-anchor="middle" font-size="18" font-weight="600">{label}</text>')
    parts += ['<path d="M34 455H1066" stroke="#cedde3"/>',
        '<text x="34" y="490" font-size="19" font-weight="600">Alternating neck sites, viewed from above</text>',
        '<text x="34" y="522" font-size="17">Gap 1 → A; gap 2 → B; gap 3 → A</text>',
        '<text x="34" y="552" font-size="17">The two sets are offset by π/m (half a step).</text>',
        '<text x="34" y="590" font-size="17">Each sheet continues to one conical end.</text>',
        '<text x="34" y="620" font-size="17">Outer rims and cut edges are display boundaries.</text>',
        '<text x="34" y="650" font-size="17">Neck widths and vertical separation are enlarged.</text>',
        '<circle cx="850" cy="559" r="78" fill="none" stroke="#99adb5" stroke-dasharray="4 4"/>']
    for parity, color in [(0,'#21667f'),(1,'#b76c43')]:
        for j in range(data['m']):
            angle = (2*j+parity)*math.pi/data['m']
            parts.append(f'<circle cx="{850+78*math.cos(angle):.3f}" cy="{559+78*math.sin(angle):.3f}" r="5.5" fill="{color}"/>')
    parts += ['<text x="964" y="542" font-size="18" fill="#21667f">A</text>',
        '<text x="964" y="580" font-size="18" fill="#b76c43">B</text>',
        '<path d="M34 677H1066" stroke="#cedde3"/>',
        '<text x="34" y="710" font-size="17" font-weight="600">CONSTRUCTION SCHEMATIC · not a computed self-shrinker</text>',
        '<text x="34" y="738" font-size="16">Existence requires sufficiently large m for each fixed k; the displayed counts do not specify that threshold.</text>',
        '</g></svg>']
    (OUT/'shao-zou-stacking.svg').write_text('\n'.join(parts)+'\n')


def main():
    radius, residual = balanced_radius(); audits = {}
    for k in LAYERS:
        for m in COUNTS:
            data, audit = make_mesh(k, m, radius)
            name = 'shao-zou-stacking' + ('' if (k,m)==(4,10) else f'-{k}-{m}')
            (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',',':'))+'\n')
            audits[f'{k}-{m}'] = audit
            print(k, m, audit['vertices'], audit['genus'], flush=True)
            if (k,m)==(4,10): drawing(data)
    (OUT/'shao-zou-audit.json').write_text(json.dumps(dict(status='schematic',
        source='https://arxiv.org/abs/2507.18825v1', balanced_radius=radius,
        radius_balance_residual=residual, models=audits), indent=2)+'\n')


if __name__ == '__main__':
    main()
