"""Original doubled-plane topology drawing, NOT a computed self-shrinker.

Source: Ketover, arXiv:2407.01240v2, Section 2.1, Proposition 7.4 and
Section 8. See documentation/ketover-picture.md for the modeling choices.
Requires numpy, scikit-image and fast-simplification.
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
GENERA = [1, 3, 5, 11]
RING = 2.2
RIM = 4.6


def parameters(genus):
    n = genus + 1
    return min(.64, .84 * RING * math.sin(math.pi/n)), min(1, (6/n)**.55)


def field(x, y, z, genus):
    width, scale = parameters(genus)
    r2 = x*x + y*y
    height = scale*(.48 + .35*np.exp(-r2/1.7) + .19*(np.sqrt(1+r2)-1))
    dents = 0
    for j in range(genus+1):
        angle = 2*math.pi*j/(genus+1)
        d2 = (x-RING*math.cos(angle))**2 + (y-RING*math.sin(angle))**2
        dents = dents + 1.8*np.exp(-d2/width**2)
    return z*z - height*height*(1-dents)


def make_mesh(genus):
    x = np.linspace(-4.85, 4.85, 222)
    z = np.linspace(-1.7, 1.7, 120)
    X, Y, Z = np.meshgrid(x, x, z, indexing='ij', sparse=True)
    values = field(X, Y, Z, genus)
    vertices, faces, _, _ = marching_cubes(values.astype(np.float32), 0,
        spacing=(x[1]-x[0], x[1]-x[0], z[1]-z[0]), allow_degenerate=False)
    vertices += [x[0], x[0], z[0]]
    vertices, faces = fast_simplification.simplify(vertices, faces,
        target_count=18000, agg=5)
    vertices, faces = clip_disk(vertices, faces, RIM)
    rim = np.abs(np.linalg.norm(vertices[:, :2], axis=1)-RIM) < 1e-5
    def gradient(p):
        eps = 1e-4
        return np.column_stack([(field(*(p+np.eye(3)[i]*eps).T, genus)
            - field(*(p-np.eye(3)[i]*eps).T, genus))/(2*eps) for i in range(3)])
    for _ in range(4):
        grad = gradient(vertices)
        vertices[~rim] -= ((field(*vertices.T, genus)/np.sum(grad*grad, axis=1))[:, None]*grad)[~rim]
    # Preserve the circular display boundary while correcting its height.
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
    return dict(name='ketover-shrinkers', kind='ketover-schematic', status='schematic',
        genus=genus, vertices=np.round(vertices, 6).tolist(),
        normals=np.round(normals, 6).tolist(), faces=faces.tolist(), paths=[],
        view=dict(yaw=.16, pitch=.55, radius=4.9), genera=GENERA,
        ring_radius=RING, display_radius=RIM,
        description='Original two-sheet model with g+1 necks. Not a computed shrinker. '
        'Two ends are proved only for sufficiently large genus; no threshold is asserted.'), audit


def drawing(data):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 640" role="img" aria-labelledby="title desc">',
        '<title id="title">Ketover doubled planes: two sheets joined by six necks</title>',
        '<desc id="desc">Original genus-five topology schematic. Six smooth necks arranged around a circle join upper and lower sheets, each continuing to a conical end. A vertical cutaway reveals the gap and neck walls. No shrinker equation has been solved; two ends are proved only for sufficiently large genus.</desc>',
        '<rect width="1000" height="640" fill="#f7fafb"/>',
        '<g font-family="Arial, sans-serif" fill="#183f52">',
        '<text x="32" y="43" font-size="28" font-weight="600">Two sheets, joined through a ring of necks</text>',
        '<text x="32" y="75" font-size="17" fill="#5b7480">Ketover doubled planes · genus 5 illustration · 6 necks</text>']
    vertices = np.array(data['vertices']); faces = np.array(data['faces'])
    normals = np.array(data['normals'])
    for cx, cut in [(250, False), (750, True)]:
        yaw, pitch = .16, .55
        cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
        rotation = np.array([[cy, -sy, 0], [-sy*sp, -cy*sp, cp], [sy*cp, cy*cp, sp]])
        q = vertices @ rotation.T; ns = normals @ rotation.T
        xy = np.column_stack([cx+48*q[:, 0], 260-48*q[:, 1]])
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
                    ya, yb = vertices[ia, 1], vertices[ib, 1]
                    if ya <= 0: polygon.append(xy[ia])
                    if (ya <= 0) != (yb <= 0):
                        polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(polygon) < 3: continue
            points = ' '.join(f'{p[0]:.2f},{p[1]:.2f}' for p in polygon)
            parts.append(f'<polygon points="{points}" fill="{color}" stroke="{color}" stroke-width=".7"/>')
        label = 'Cutaway: the sheets meet along the neck walls' if cut else 'One connected surface; both sheets continue outward'
        parts.append(f'<text x="{cx}" y="445" text-anchor="middle" font-size="17" font-weight="600">{label}</text>')
    parts += ['<path d="M32 472H968" stroke="#ccdce3"/>',
        '<text x="32" y="504" font-size="18">g + 1 bridges between two punctured planes give genus g and two ends.</text>',
        '<text x="32" y="534" font-size="16">Blue and gold distinguish the two sides of the surface. Outer rims and cut edges are display boundaries.</text>',
        '<text x="32" y="576" font-size="17" font-weight="600">SCHEMATIC · no exact formula or numerical solution of the shrinker equation</text>',
        '<text x="32" y="606" font-size="16">Two ends are proved only for sufficiently large genus; this drawing does not specify a threshold.</text>',
        '</g></svg>']
    (OUT/'ketover-shrinkers.svg').write_text('\n'.join(parts)+'\n')


def main():
    audits = {}
    for genus in GENERA:
        data, audits[str(genus)] = make_mesh(genus)
        name = 'ketover-shrinkers' if genus == 5 else f'ketover-shrinkers-{genus}'
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
        if genus == 5: drawing(data)
    (OUT/'ketover-audit.json').write_text(json.dumps(dict(status='schematic',
        source='https://arxiv.org/pdf/2407.01240v2',
        source_locations='Section 2.1; Proposition 7.4, pp. 36–37; Section 8, pp. 37–42',
        resolution=[222, 222, 120], display_radius=RIM, models=audits), indent=2)+'\n')
    print(json.dumps(audits, indent=2))


if __name__ == '__main__': main()
