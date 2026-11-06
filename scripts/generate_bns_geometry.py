"""Original BNS topology illustration; NOT a numerical self-shrinker.

Read documentation/bns-picture.md for the implicit drawing equation and its
relation to BNS Figures 3–4. Requires numpy, scikit-image, fast-simplification.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json
import math
import numpy as np
from skimage.measure import marching_cubes
import fast_simplification

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
GENERA = [1, 2, 3, 5, 11]


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


def field(x, y, z, genus):
    n = genus + 1
    r2 = x*x + y*y
    # Smooth at r=0: r^n sin(n theta) = Im((x+iy)^n).
    # The radial factor tends to r^(3-n), giving an illustrative conical end.
    wave = np.imag((x + 1j*y)**n) * (r2 + 1)**((3-n)/2)
    amplitude = 1.35 / n**1.65
    return z*(r2 + z*z - 4) - amplitude*wave


def make_mesh(genus):
    x = np.linspace(-5.3, 5.3, 222)
    z = np.linspace(-3.3, 3.3, 160)
    X, Y, Z = np.meshgrid(x, x, z, indexing='ij', sparse=True)
    values = field(X, Y, Z, genus)
    vertices, faces, _, _ = marching_cubes(values.astype(np.float32), 0,
        spacing=(x[1]-x[0], x[1]-x[0], z[1]-z[0]), allow_degenerate=False)
    vertices += [x[0], x[0], z[0]]
    vertices, faces = fast_simplification.simplify(vertices, faces,
        target_count=16000, agg=5)
    vertices, faces = clip_disk(vertices, faces, 5)
    # Reproject simplification vertices onto the implicit illustration, then
    # restore the display rim. This is NOT a shrinker PDE iteration.
    rim = np.abs(np.linalg.norm(vertices[:, :2], axis=1)-5) < 1e-5
    def gradient(p):
        eps = 1e-4
        return np.column_stack([(field(*(p+np.eye(3)[i]*eps).T, genus)
            - field(*(p-np.eye(3)[i]*eps).T, genus))/(2*eps) for i in range(3)])
    for _ in range(3):
        grad = gradient(vertices)
        step = field(*vertices.T, genus) / np.sum(grad*grad, axis=1)
        vertices[~rim] -= (step[:, None]*grad)[~rim]
    normals = gradient(vertices)
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    a, b, c = vertices[faces[:, 0]], vertices[faces[:, 1]], vertices[faces[:, 2]]
    reverse = np.sum(np.cross(b-a, c-a)*normals[faces].mean(axis=1), axis=1) < 0
    faces[reverse] = faces[reverse][:, [0, 2, 1]]
    audit = topology(vertices, faces)
    assert audit['components'] == 1 and audit['boundary_loops'] == 1, audit
    assert audit['genus'] == genus and audit['edge_incidence'] == [1, 2], audit
    assert audit['boundary_is_manifold'], audit
    return dict(name='bns-shrinkers', kind='bns-schematic', status='schematic',
        genus=genus, vertices=np.round(vertices, 6).tolist(),
        normals=np.round(normals, 6).tolist(), faces=faces.tolist(), paths=[],
        view=dict(yaw=.22, pitch=.45, radius=5.3), genera=GENERA,
        description='Original topology schematic informed by BNS Figures 3–4; '
        'not a computed self-shrinker. The one-ended low-genus shape is conjectural.'), audit


def drawing(data):
    """A standalone full-surface/cutaway SVG from the same genus-three mesh."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 640" role="img" aria-labelledby="title desc">',
        '<title id="title">Buzano–Nguyen–Schulz: surface and interior</title>',
        '<desc id="desc">Original genus-three topology schematic inspired by Figures 3 and 4. '
        'A rounded cap and a central sheet connect through alternating openings to one outer sheet. '
        'The right view removes the front half to expose the interior. Not a computed self-shrinker.</desc>',
        '<rect width="1000" height="640" fill="#f7fafb"/>',
        '<g font-family="Arial, sans-serif" fill="#183f52">',
        '<text x="34" y="44" font-size="27" font-weight="600">A surface with handles, and a sheet through its center</text>',
        '<text x="34" y="76" font-size="17" fill="#5b7480">Buzano–Nguyen–Schulz · genus 3 illustration · after Figures 3–4</text>']
    vertices = np.array(data['vertices']); faces = np.array(data['faces'])
    for cx, cut in [(250, False), (750, True)]:
        yaw, pitch = .22, .48
        x, y, z = vertices.T
        a=x*np.cos(yaw)-y*np.sin(yaw); b=x*np.sin(yaw)+y*np.cos(yaw)
        q=np.column_stack([a, z*np.cos(pitch)-b*np.sin(pitch), z*np.sin(pitch)+b*np.cos(pitch)])
        xy=np.column_stack([cx+44*q[:, 0], 282-44*q[:, 1]])
        for j in np.argsort(q[faces, 2].mean(axis=1)):
            f=faces[j]
            a,b,c=q[f]; n=np.cross(b-a,c-a); n/=max(np.linalg.norm(n),1e-12)
            palette = [218, 171, 75] if n[2]<0 else [65, 105, 132]
            if n[2]<0: n=-n
            light=.48+.48*max(0,n @ np.array([-.35,.55,.76]))
            rgb=[round(v*light) for v in palette]
            polygon = list(xy[f])
            if cut:
                polygon = []
                for ia, ib in zip(f, np.roll(f, -1)):
                    ya, yb = vertices[ia, 1], vertices[ib, 1]
                    if ya <= 0: polygon.append(xy[ia])
                    if (ya <= 0) != (yb <= 0):
                        polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(polygon) < 3: continue
            points=' '.join(f'{p[0]:.2f},{p[1]:.2f}' for p in polygon)
            color=f'rgb({",".join(map(str,rgb))})'
            parts.append(f'<polygon points="{points}" fill="{color}" stroke="{color}" stroke-width=".35"/>')
        parts.append(f'<text x="{cx}" y="438" text-anchor="middle" font-size="19" font-weight="600">'
            f'{"Front half removed: central sheet exposed" if cut else "One connected surface, with one outer sheet"}</text>')
    parts += ['<path d="M34 470H966" stroke="#ccdce3"/>',
        '<text x="34" y="502" font-size="17">Gold and blue show the two sides of the same surface.</text>',
        '<text x="34" y="533" font-size="17">Outer rim and cut edges are display boundaries; the surface continues to infinity.</text>',
        '<text x="34" y="572" font-size="17" font-weight="600">SCHEMATIC · not an exact formula or a numerical solution of the shrinker equation</text>',
        '<text x="34" y="603" font-size="16">One end is proved for sufficiently large genus; Figures 3–4 supply numerical evidence at low genus.</text>',
        '</g></svg>']
    (OUT/'bns-shrinkers.svg').write_text('\n'.join(parts)+'\n')


def main():
    audit = {}
    for g in GENERA:
        data, audit[str(g)] = make_mesh(g)
        name = 'bns-shrinkers' if g == 3 else f'bns-shrinkers-{g}'
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
        if g == 3: drawing(data)
    (OUT/'bns-audit.json').write_text(json.dumps(dict(status='schematic',
        source='https://arxiv.org/pdf/2110.06027v2',
        source_locations='Lemma 2.2; Theorems 1.2–1.3; Section 4, Figures 3–4',
        resolution=[222, 222, 160], display_radius=5, models=audit), indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__': main()
