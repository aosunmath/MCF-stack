"""HMW sphere–plane topology picture, not a computed self-shrinker.

Source: arXiv:2502.20340v3, Figures 1, 5–6 and Theorems 40–42.
See documentation/hmw-sphere-plane-picture.md. Requires the same optional geometry
libraries as generate_bns_geometry.py, plus Pillow.
"""
from pathlib import Path
import base64
import io
import json
import numpy as np
from PIL import Image, ImageDraw

# Reuse an explicitly illustrative implicit surface, not a BNS shrinker.
# This does not identify the shrinkers produced by the two existence proofs.
from generate_bns_geometry import make_mesh, clip_disk, topology, field

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
GENERA = [3, 5, 11]
RADIUS = 3.8


def surface(genus):
    data, _ = make_mesh(genus)
    v, f = clip_disk(np.array(data['vertices']), np.array(data['faces']), RADIUS)
    eps = 1e-4
    normal = np.column_stack([(field(*(v+eps*np.eye(3)[i]).T, genus)
        - field(*(v-eps*np.eye(3)[i]).T, genus))/(2*eps) for i in range(3)])
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    audit = topology(v, f)
    assert audit['components'] == 1 and audit['boundary_loops'] == 1, audit
    assert audit['genus'] == genus and audit['boundary_is_manifold'], audit
    data.update(name='hmw-one-ended', kind='hmw-sphere-plane-schematic',
        genus=genus, genera=GENERA, vertices=np.round(v, 6).tolist(),
        normals=np.round(normal, 6).tolist(), faces=f.tolist(),
        view=dict(yaw=.20, pitch=.38, radius=4.0),
        description='Original HMW topology schematic informed by Figures 1, 5–6. '
        'Not a computed shrinker or a reproduction of the numerical source figures. '
        'The illustrated one-ended shape is not proved for every displayed genus.',
        drawing=dict(display_radius=RADIUS, n=genus+1,
            amplitude=1.35/(genus+1)**1.65))
    return data, audit


def limit():
    """Triangulate the exact limiting configuration S²(2) union {z=0}."""
    v, normal, faces = [], [], []
    segments, rings = 144, 64
    v.append([0, 0, 2]); normal.append([0, 0, 1])
    for j in range(1, rings):
        phi = np.pi*j/rings
        for k in range(segments):
            theta = 2*np.pi*k/segments
            p = [np.sin(phi)*np.cos(theta), np.sin(phi)*np.sin(theta), np.cos(phi)]
            v.append([2*a for a in p]); normal.append(p)
    bottom = len(v); v.append([0, 0, -2]); normal.append([0, 0, -1])
    for k in range(segments):
        q = (k+1) % segments
        faces.append([0, 1+k, 1+q])
        for j in range(rings-2):
            a, b = 1+j*segments+k, 1+j*segments+q
            faces.extend([[a, a+segments, b+segments], [a, b+segments, b]])
        faces.append([bottom, 1+(rings-2)*segments+q, 1+(rings-2)*segments+k])
    center = len(v); v.append([0, 0, 0]); normal.append([0, 0, 1])
    for k in range(segments):
        theta = 2*np.pi*k/segments
        v.append([RADIUS*np.cos(theta), RADIUS*np.sin(theta), 0]); normal.append([0, 0, 1])
        faces.append([center, center+1+k, center+1+(k+1) % segments])
    return dict(name='hmw-sphere-plane-limit', kind='hmw-limit',
        status='exact-configuration-mesh', vertices=np.round(v, 7).tolist(),
        normals=np.round(normal, 7).tolist(), faces=faces, paths=[],
        view=dict(yaw=.20, pitch=.38, radius=4.0),
        description='Radius-two sphere and horizontal plane, each with multiplicity one. '
        'The intersection circle is singular; this is the large-genus limit, not a finite-genus surface.')


def render(painter, data, center, scale, cut=False):
    v, f = np.array(data['vertices']), np.array(data['faces'])
    yaw, pitch = .20, .43 if cut else .38
    def project(p):
        x, y, z = p.T
        a = x*np.cos(yaw)-y*np.sin(yaw); b = x*np.sin(yaw)+y*np.cos(yaw)
        return np.column_stack([a, z*np.cos(pitch)-b*np.sin(pitch), z*np.sin(pitch)+b*np.cos(pitch)])
    q = project(v)
    for j in np.argsort(q[f, 2].mean(axis=1)):
        face = f[j]; poly = list(v[face])
        if cut:
            poly = []
            for a, b in zip(v[face], np.roll(v[face], -1, axis=0)):
                if a[1] <= 0: poly.append(a)
                if a[1]*b[1] < 0: poly.append(a+(b-a)*a[1]/(a[1]-b[1]))
            if len(poly) < 3: continue
        a, b, c = q[face]; n = np.cross(b-a, c-a); n /= max(np.linalg.norm(n), 1e-12)
        color = np.array([218, 169, 80] if n[2] < 0 else [77, 135, 162])
        if n[2] < 0: n = -n
        light = .50+.48*max(0, n@np.array([-.35, .55, .76]))
        rgb = tuple(np.rint(color*light).astype(int))+(255,)
        p = project(np.array(poly))
        screen = np.column_stack([center[0]+scale*p[:, 0], center[1]-scale*p[:, 1]])
        painter.polygon([tuple(np.rint(3*a).astype(int)) for a in screen], fill=rgb)


def drawing(data, limiting):
    picture = Image.new('RGBA', (3300, 2400)); painter = ImageDraw.Draw(picture)
    render(painter, data, (275, 272), 64)
    render(painter, data, (825, 272), 64, True)
    render(painter, limiting, (210, 605), 39)
    buffer = io.BytesIO()
    picture.resize((2200, 1600), Image.Resampling.LANCZOS).save(buffer, format='PNG', optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 800" role="img" aria-labelledby="title desc">',
        '<title id="title">Hoffman–Martín–White sphere–plane shrinkers: handles and interior</title>',
        '<desc id="desc">Original genus-five topology schematic, full surface and cutaway. Alternating openings connect the caps to a central sheet and exterior. A separate inset shows the intersecting sphere–plane limit. The finite-genus drawing is not a computed shrinker.</desc>',
        '<rect width="1100" height="800" fill="#f7fafb"/>',
        f'<image width="1100" height="800" href="data:image/png;base64,{encoded}"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        '<text x="38" y="47" font-size="28" font-weight="600">Hoffman–Martín–White sphere–plane shrinkers</text>',
        '<text x="38" y="79" font-size="18" fill="#58727e">Genus 5 topology model · informed by Figures 1, 5 and 6 · not a computed shrinker</text>',
        '<text x="275" y="440" text-anchor="middle" font-size="20" font-weight="600">One connected surface with handles</text>',
        '<text x="825" y="440" text-anchor="middle" font-size="20" font-weight="600">Cutaway: inner sheet and lower cap</text>',
        '<text x="38" y="480" font-size="17">Gold and blue distinguish the two sides. All outer rims and cut edges are artificial.</text>',
        '<path d="M38 505H1062" stroke="#ccdce3"/>',
        '<text x="210" y="720" text-anchor="middle" font-size="18" font-weight="600">Separate limit: plane ∪ S²(2)</text>',
        '<text x="430" y="550" font-size="20" font-weight="600">What the paper establishes</text>',
        '<text x="430" y="585" font-size="18">Σg ∩ {z = 0} consists of g + 1 equally spaced lines.</text>',
        '<text x="430" y="620" font-size="18">Genus g exists for every g ≥ 1.</text>',
        '<text x="430" y="655" font-size="18">Exactly one end is proved for sufficiently large g.</text>',
        '<text x="430" y="690" font-size="18">As g → ∞, the limit is a sphere of radius 2 and a plane.</text>',
        '<text x="38" y="768" font-size="17" font-weight="600">SCHEMATIC · finite-genus shape and cone slope are illustrative · no shrinker PDE has been solved</text>',
        '</g></svg>']
    (OUT/'hmw-one-ended.svg').write_text('\n'.join(svg)+'\n')


def main():
    audits = {}; limiting = limit()
    (OUT/'hmw-sphere-plane-limit.json').write_text(json.dumps(limiting, separators=(',', ':'))+'\n')
    for g in GENERA:
        data, audits[str(g)] = surface(g)
        name = 'hmw-one-ended' if g == 5 else f'hmw-one-ended-{g}'
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
        if g == 5: drawing(data, limiting)
    audit = dict(status='schematic', source='https://arxiv.org/abs/2502.20340v3',
        source_locations='Figures 1, 5–6; Section 5; Theorems 40–42; Lemma 64',
        display_radius=RADIUS, models=audits)
    (OUT/'hmw-sphere-plane-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(json.dumps(audits, indent=2))


if __name__ == '__main__': main()
