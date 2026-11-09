"""Original Ilmanen–White illustration, NOT a numerical self-shrinker.

See documentation/ilmanen-white-picture.md for source passages and the drawing
equation. Requires numpy, scikit-image and fast-simplification.
"""
from pathlib import Path
import json
import math
import numpy as np
from skimage.measure import marching_cubes
import fast_simplification
from generate_bns_geometry import clip_disk, topology

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
GENERA = [2, 3, 5, 11]
RING, RIM = 2.0, 4.6


def field(x, y, z, genus):
    n = genus + 1
    width = min(.92, .80 * RING * math.sin(math.pi/n))
    scale = min(1, (4/n)**.65)
    r2 = x*x + y*y
    # Smooth at the axis; asymptotically n-fold, rather than round, cone links.
    wave = np.real(((x + 1j*y) / np.sqrt(r2 + RING**2))**n)
    height = scale*(.48 + .50*np.exp(-r2/1.7) + .27*(np.sqrt(1+r2)-1))*(1-.12*wave)
    dents = 0
    for j in range(n):
        angle = 2*math.pi*j/n
        d2 = (x-RING*math.cos(angle))**2 + (y-RING*math.sin(angle))**2
        dents = dents + 1.8*np.exp(-d2/width**2)
    return z*z - height*height*(1-dents)


def equator_segments(vertices, faces):
    """Intersection with z=0 of the displayed triangles, not a separate object."""
    segments = []
    for face in faces:
        points = []
        for a, b in zip(face, np.roll(face, -1)):
            p, q = vertices[a], vertices[b]
            if (p[2] < 0) != (q[2] < 0):
                point = p + p[2]/(p[2]-q[2])*(q-p)
                point[2] = 0
                points.append(point.tolist())
        if points:
            assert len(points) == 2
            segments.append(points)
    return np.round(segments, 6).tolist()


def make_mesh(genus):
    x = np.linspace(-4.85, 4.85, 222)
    z = np.linspace(-2.1, 2.1, 140)
    X, Y, Z = np.meshgrid(x, x, z, indexing='ij', sparse=True)
    values = field(X, Y, Z, genus)
    vertices, faces, _, _ = marching_cubes(values.astype(np.float32), 0,
        spacing=(x[1]-x[0], x[1]-x[0], z[1]-z[0]), allow_degenerate=False)
    vertices += [x[0], x[0], z[0]]
    vertices, faces = fast_simplification.simplify(vertices, faces,
        target_count=20000, agg=5)
    vertices, faces = clip_disk(vertices, faces, RIM)
    rim = np.abs(np.linalg.norm(vertices[:, :2], axis=1)-RIM) < 1e-5

    def gradient(p):
        eps = 1e-4
        return np.column_stack([(field(*(p+np.eye(3)[i]*eps).T, genus)
            - field(*(p-np.eye(3)[i]*eps).T, genus))/(2*eps) for i in range(3)])

    for _ in range(4):
        grad = gradient(vertices)
        vertices[~rim] -= ((field(*vertices.T, genus)/np.sum(grad*grad, axis=1))[:, None]*grad)[~rim]
    vertices[rim, 2] = np.sign(vertices[rim, 2])*np.sqrt(-field(*np.column_stack([
        vertices[rim, :2], np.zeros(rim.sum())]).T, genus))
    normals = gradient(vertices)
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    a, b, c = vertices[faces[:, 0]], vertices[faces[:, 1]], vertices[faces[:, 2]]
    reverse = np.sum(np.cross(b-a, c-a)*normals[faces].mean(axis=1), axis=1) < 0
    faces[reverse] = faces[reverse][:, [0, 2, 1]]
    audit = topology(vertices, faces)
    assert audit['components'] == 1 and audit['boundary_loops'] == 2, audit
    assert audit['genus'] == genus and audit['edge_incidence'] == [1, 2], audit
    assert audit['boundary_is_manifold'], audit
    return dict(name='iw-two-ended', kind='iw-schematic', status='schematic',
        genus=genus, vertices=np.round(vertices, 6).tolist(),
        normals=np.round(normals, 6).tolist(), faces=faces.tolist(), paths=[],
        equator=equator_segments(vertices, faces),
        view=dict(yaw=math.pi/4, pitch=.28, radius=4.9), genera=GENERA,
        display_radius=RIM,
        description='Original Ilmanen–White topology schematic informed by Figure 1, '
        'Theorem 4.8 and Theorem 7.6. Genus h, h+1 neck curves and two ends. '
        'Not a computed shrinker or a reconstruction of Chopp’s numerical surface.'), audit


def drawing(data):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 640" role="img" aria-labelledby="title desc">',
        '<title id="title">Ilmanen–White: two conical ends joined through four necks</title>',
        '<desc id="desc">Original genus-three schematic informed by Figure 1 and the graph description in the paper. '
        'An upper graph and its reflection join along four closed neck curves in the horizontal plane. '
        'The cutaway exposes the neck walls. Each outer rim continues to a conical end. Not a computed shrinker.</desc>',
        '<rect width="1000" height="640" fill="#f7fafb"/>',
        '<g font-family="Arial, sans-serif" fill="#183f52">',
        '<text x="32" y="43" font-size="28" font-weight="600">Two conical ends, joined through four necks</text>',
        '<text x="32" y="75" font-size="17" fill="#5b7480">Ilmanen–White · genus h = 3 · the paper’s wheel parameter is g = 4</text>']
    vertices, faces = np.array(data['vertices']), np.array(data['faces'])
    normals = np.array(data['normals'])
    for cx, cut in [(250, False), (750, True)]:
        yaw, pitch = (math.pi/4, .28) if not cut else (math.pi/4, .38)
        cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
        rotation = np.array([[cy, -sy, 0], [-sy*sp, -cy*sp, cp], [sy*cp, cy*cp, sp]])
        q, ns = vertices @ rotation.T, normals @ rotation.T
        xy = np.column_stack([cx+48*q[:, 0], 266-48*q[:, 1]])
        for j in np.argsort(q[faces, 2].mean(axis=1)):
            f = faces[j]; n = ns[f].mean(axis=0); n /= np.linalg.norm(n)
            palette = [69, 137, 159] if n[2] >= 0 else [209, 154, 81]
            if n[2] < 0: n = -n
            light = .50+.48*max(0, n @ np.array([-.35, .55, .76]))
            color = 'rgb('+','.join(str(round(v*light)) for v in palette)+')'
            polygon = list(xy[f])
            if cut:
                polygon = []
                for ia, ib in zip(f, np.roll(f, -1)):
                    ya, yb = vertices[ia, :2].sum(), vertices[ib, :2].sum()
                    if ya <= 0: polygon.append(xy[ia])
                    if (ya <= 0) != (yb <= 0):
                        polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(polygon) < 3: continue
            points = ' '.join(f'{p[0]:.2f},{p[1]:.2f}' for p in polygon)
            parts.append(f'<polygon points="{points}" fill="{color}" stroke="{color}" stroke-width=".6"/>')
        label = 'Cutaway: upper and lower graphs meet at the necks' if cut else 'One connected surface, with two outward ends'
        parts.append(f'<text x="{cx}" y="435" text-anchor="middle" font-size="17" font-weight="600">{label}</text>')
    parts += ['<path d="M32 466H968" stroke="#ccdce3"/>',
        '<text x="32" y="500" font-size="18">h + 1 neck curves in z = 0 give genus h; both ends are asymptotically conical.</text>',
        '<text x="32" y="532" font-size="16">Blue and gold show opposite sides of one surface. Outer rims and cut edges are display boundaries.</text>',
        '<text x="32" y="574" font-size="17" font-weight="600">SCHEMATIC · the shrinker equation has not been solved</text>',
        '<text x="32" y="605" font-size="16">After Ilmanen–White, Figure 1 and Theorems 4.8, 7.6. Neck shapes, scale and cone slopes are illustrative.</text>',
        '</g></svg>']
    (OUT/'iw-two-ended.svg').write_text('\n'.join(parts)+'\n')


def main():
    audits = {}
    for genus in GENERA:
        data, audits[str(genus)] = make_mesh(genus)
        name = 'iw-two-ended' if genus == 3 else f'iw-two-ended-{genus}'
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
        if genus == 3: drawing(data)
    (OUT/'iw-audit.json').write_text(json.dumps(dict(status='schematic',
        source='https://arxiv.org/pdf/2406.18703v3',
        source_locations='Figure 1, p. 2; Theorem 4.8 and Corollary 4.9, pp. 10–11; '
        'Theorem 7.6, pp. 20–21; Lemmas 9.1, 9.3 and Theorem 9.4, pp. 25–26',
        resolution=[222, 222, 140], display_radius=RIM, models=audits), indent=2)+'\n')
    print(json.dumps(audits, indent=2))


if __name__ == '__main__': main()
