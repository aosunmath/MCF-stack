"""Scherk-based KKM construction illustration, NOT a solved self-shrinker.

Requires NumPy, scikit-image, fast-simplification. See documentation/kkm-picture.md.
The source equation is KKM (5.1), arXiv:1106.5454v3, p. 9. The global
coordinate map and end shear below are drawing choices, not the paper's
matched initial surface or its nonlinear correction.
"""
from pathlib import Path
from collections import Counter, defaultdict
from html import escape
import json
import math
import numpy as np
from skimage.measure import marching_cubes
import fast_simplification

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
PALETTE = [[78, 145, 170], [206, 140, 82], [110, 163, 177]]


def topology(vertices, faces):
    edges = Counter(tuple(sorted((int(f[i]), int(f[(i+1) % 3]))))
                    for f in faces for i in range(3))
    neighbors, boundary = defaultdict(set), defaultdict(set)
    for (a, b), count in edges.items():
        neighbors[a].add(b); neighbors[b].add(a)
        if count == 1:
            boundary[a].add(b); boundary[b].add(a)
    def components(graph):
        remaining, count = set(graph), 0
        while remaining:
            pending = [remaining.pop()]; count += 1
            while pending:
                for b in graph[pending.pop()] & remaining:
                    remaining.remove(b); pending.append(b)
        return count
    chi = len(vertices)-len(edges)+len(faces)
    loops = components(boundary)
    return dict(vertices=len(vertices), faces=len(faces),
                components=components(neighbors), boundary_loops=loops,
                boundary_is_manifold=all(len(v) == 2 for v in boundary.values()),
                edge_incidence=sorted(set(edges.values())), euler_characteristic=chi,
                genus=(2-loops-chi)//2)


def clip_disk(vertices, faces, radius):
    """Clip triangle edges to a circular display boundary, sharing cut vertices."""
    points = vertices.tolist(); result = []; cuts = {}
    inside = np.linalg.norm(vertices[:, :2], axis=1) <= radius
    def crossing(a, b):
        key = tuple(sorted((a, b)))
        if key not in cuts:
            p, q = vertices[a], vertices[b]; d = q-p
            A = d[:2] @ d[:2]; B = 2*(p[:2] @ d[:2])
            C = p[:2] @ p[:2]-radius**2
            roots = [(-B+s*math.sqrt(max(0, B*B-4*A*C)))/(2*A) for s in (-1, 1)]
            t = next(t for t in roots if -1e-7 <= t <= 1+1e-7)
            cuts[key] = len(points); points.append((p+t*d).tolist())
        return cuts[key]
    for face in faces.tolist():
        polygon = []
        for a, b in zip(face, face[1:]+face[:1]):
            if inside[a]: polygon.append(a)
            if inside[a] != inside[b]: polygon.append(crossing(a, b))
        for i in range(1, len(polygon)-1):
            result.append([polygon[0], polygon[i], polygon[i+1]])
    used = sorted({i for f in result for i in f}); lookup = {old: i for i, old in enumerate(used)}
    return np.array(points)[used], np.array([[lookup[i] for i in f] for f in result])


def make_mesh(k, resolution=181, target=16000):
    # The map r=2 exp(u/k) sech(v/k), z=2 tanh(v/k) sends
    # u=0 to S^2(2), v=0 to the plane, and the periodic axis to the equator.
    x = np.linspace(-3.95, 3.95, resolution)
    z = np.linspace(-2.12, 2.12, 108)
    X, Y, Z = np.meshgrid(x, x, z, indexing='ij', sparse=True)
    r = np.sqrt(X*X+Y*Y)
    V = k*np.arctanh(np.clip(Z/2, -.99999999, .99999999))
    U = k*np.log(np.maximum(r, 1e-12)/2/np.sqrt(np.maximum(1-(Z/2)**2, 1e-16)))
    wave = np.sin(k*np.arctan2(Y, X))
    # A bounded form of sinh(U) sinh(V) = sin(k theta).
    field = np.tanh(U)*np.tanh(V)-wave/np.cosh(np.clip(U, -100, 100))/np.cosh(V)
    field = np.where(np.abs(Z) >= 2, np.sign(Z), field)
    vertices, faces, _, _ = marching_cubes(field.astype(np.float32), 0,
        spacing=(x[1]-x[0], x[1]-x[0], z[1]-z[0]), allow_degenerate=False)
    vertices += [x[0], x[0], z[0]]
    vertices, faces = fast_simplification.simplify(vertices, faces, target_count=target, agg=5)
    vertices, faces = clip_disk(vertices, faces, 3.65)
    audit = topology(vertices, faces)
    assert audit['components'] == 1 and audit['boundary_loops'] == 1, audit
    assert audit['boundary_is_manifold'] and audit['edge_incidence'] == [1, 2], audit
    assert audit['genus'] == k-1, audit
    centers = vertices[faces].mean(axis=1)
    groups = np.where(np.abs(centers[:, 2]) > .65, 0,
                      np.where(np.abs(np.linalg.norm(centers[:, :2], axis=1)-2) < .48, 1, 2))
    def smooth(t):
        t=np.clip(t,0,1); return t*t*(3-2*t)
    exterior=smooth((np.linalg.norm(centers[:, :2],axis=1)-2.4)/.5)
    belt=smooth((.95-np.abs(centers[:, 2]))/.5)*smooth((.75-np.abs(np.linalg.norm(centers[:, :2],axis=1)-2))/.4)
    colors=(1-exterior[:,None])*np.array(PALETTE[0])+exterior[:,None]*np.array(PALETTE[2])
    colors=(1-belt[:,None])*colors+belt[:,None]*np.array(PALETTE[1])
    # Optional shear is applied by the viewer; it is a free illustrative cone.
    r = np.linalg.norm(vertices[:, :2], axis=1)
    t = np.clip((r-2.35)/.85, 0, 1)
    weights = r*np.sin(k*np.arctan2(vertices[:, 1], vertices[:, 0]))*t*t*t*(10-15*t+6*t*t)
    data = dict(name='kkm-shrinker', status='schematic', vertices=np.round(vertices, 6).tolist(),
                faces=faces.tolist(), paths=[], palette=PALETTE, faceGroups=groups.tolist(),
                faceColors=np.round(colors).astype(int).tolist(),
                view=dict(pitch=.32, yaw=.42, radius=3.8),
                construction=dict(kind='kkm', periods=k, genus=k-1,
                                  endWeights=np.round(weights, 7).tolist(), amplitude=.075),
                description='Scherk-based construction schematic in R3; not a numerical KKM self-shrinker.')
    return data, audit


def drawing(data):
    """Original vector drawing of the same mesh, with an explanatory cutaway."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="680" viewBox="0 0 1000 680" role="img" aria-labelledby="title desc">',
        '<title id="title">KKM shrinker: a Scherk-based construction picture</title>',
        '<desc id="desc">Two views of one connected illustrative surface: spherical caps, an inner disk and an outer sheet joined by a periodic Scherk belt. The cutaway exposes the interior. This is not a solved shrinker.</desc>',
        '<rect width="1000" height="680" fill="#f7fafb"/>',
        '<g font-family="Arial, sans-serif" fill="#183f52">',
        '<text x="38" y="47" font-size="27" font-weight="600">Kapouleas–Kleene–Møller shrinkers</text>',
        '<text x="38" y="77" font-size="17" fill="#5b7480">Sphere–plane desingularization through a periodic Scherk belt</text>']
    vertices = np.array(data['vertices'])
    vertices[:, 2] += data['construction']['amplitude']*np.array(data['construction']['endWeights'])
    faces = np.array(data['faces']); centers = vertices[faces].mean(axis=1)
    def clip(polygon, normal):
        result=[]
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            da,db=a[:2]@normal,b[:2]@normal
            if da<=0: result.append(a)
            if da*db<0: result.append(a+(b-a)*da/(da-db))
        return result
    for cx, yaw, pitch, cut in [(255, .42, .32, False), (750, .42, .48, True)]:
        x, y, z = vertices.T
        a=x*np.cos(yaw)-y*np.sin(yaw); b=x*np.sin(yaw)+y*np.cos(yaw)
        q=np.column_stack([a, z*np.cos(pitch)-b*np.sin(pitch), z*np.sin(pitch)+b*np.cos(pitch)])
        xy=np.column_stack([cx+60*q[:, 0], 315-60*q[:, 1]])
        order=np.argsort(q[faces, 2].mean(axis=1))
        for j in order:
            f=faces[j]; a,b,c=q[f]; n=np.cross(b-a,c-a); n/=np.linalg.norm(n)
            light=.42+.52*abs(n @ np.array([.3,.5,.8]))
            rgb=[int(base*light+255*(1-light)*.25) for base in data['faceColors'][j]]
            color=f'rgb({",".join(map(str,rgb))})'
            polygons=[vertices[f].tolist()] if not cut else [
                clip(clip(list(vertices[f]),np.array([-side,0])),np.array([-.35*side,1])) for side in [-1,1]]
            for polygon in polygons:
                if len(polygon)<3: continue
                p=np.array(polygon); x,y,z=p.T
                h=x*np.cos(yaw)-y*np.sin(yaw); depth=x*np.sin(yaw)+y*np.cos(yaw)
                pts=' '.join(f'{cx+60*a:.2f},{315-60*b:.2f}' for a,b in zip(h,z*np.cos(pitch)-depth*np.sin(pitch)))
                parts.append(f'<polygon points="{pts}" fill="{color}" stroke="{color}" stroke-width=".35"/>')
        parts.append(f'<text x="{cx}" y="490" text-anchor="middle" font-size="18" font-weight="600">{"Cutaway: inner disk and lower cap" if cut else "Connected surface with one outer sheet"}</text>')
    parts += ['<path d="M38 524H962" stroke="#cfdee4"/>',
        '<circle cx="48" cy="554" r="6" fill="#4e91aa"/><text x="63" y="560" font-size="16">Sphere-like caps</text>',
        '<circle cx="300" cy="554" r="6" fill="#ce8c52"/><text x="315" y="560" font-size="16">Scherk joining belt</text>',
        '<circle cx="566" cy="554" r="6" fill="#6ea3b1"/><text x="581" y="560" font-size="16">Inner disk and outer sheet</text>',
        '<text x="38" y="600" font-size="16">Illustration: k = 9 periods, model genus k − 1 = 8. The end waviness is illustrative.</text>',
        '<text x="38" y="630" font-size="16">The theorem applies to sufficiently large genus; no numerical threshold is asserted.</text>',
        '<text x="38" y="660" font-size="16" font-weight="600">CONSTRUCTION SCHEMATIC · not a solved self-shrinker · outer edge is a display truncation</text>',
        '</g></svg>']
    (OUT/'kkm-shrinker.svg').write_text('\n'.join(parts)+'\n')


def main():
    audit = {}
    for k in [6, 9, 12]:
        data, audit[str(k)] = make_mesh(k)
        name = 'kkm-shrinker' if k == 9 else f'kkm-shrinker-{k}'
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
        if k == 9: drawing(data)
    (OUT/'kkm-audit.json').write_text(json.dumps(dict(status='schematic',
        source='https://arxiv.org/pdf/1106.5454v3', source_equation='(5.1), p. 9',
        resolution=[181, 181, 108], display_radius=3.65, models=audit), indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__': main()
