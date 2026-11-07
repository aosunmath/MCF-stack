"""Ketover's Platonic doubling sweepouts: original construction schematics.

These meshes do not solve the shrinker equation. NumPy, SciPy and Pillow are
needed only to regenerate assets. See documentation/platonic-picture.md.
"""
from pathlib import Path
import base64
import io
import json
import math

import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw

from generate_spherical_doubling_geometry import orient_and_audit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
SOLIDS = [('tetrahedron', 4, 'T₁₂'), ('cube', 6, 'O₂₄'),
          ('octahedron', 8, 'O₂₄'), ('dodecahedron', 12, 'I₆₀'),
          ('icosahedron', 20, 'I₆₀')]
COLORS = np.array([[75, 139, 163], [211, 169, 99], [188, 116, 77]])


def face_centers(solid):
    """Outward unit face normals of the actual solid (not its vertices)."""
    phi = (1 + math.sqrt(5))/2
    cube = [(x, y, z) for x in [-1, 1] for y in [-1, 1] for z in [-1, 1]]
    if solid == 'tetrahedron':
        vertices = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    elif solid == 'cube':
        vertices = cube
    elif solid == 'octahedron':
        vertices = [tuple(s if i == j else 0 for i in range(3))
                    for j in range(3) for s in [-1, 1]]
    elif solid == 'icosahedron':
        vertices = [(0, a, b) for a in [-1, 1] for b in [-phi, phi]]
        vertices += [(z, x, y) for x, y, z in vertices] + [(y, z, x) for x, y, z in vertices]
    elif solid == 'dodecahedron':
        extra = [(0, a, b) for a in [-1/phi, 1/phi] for b in [-phi, phi]]
        vertices = cube + extra + [(z, x, y) for x, y, z in extra] + [(y, z, x) for x, y, z in extra]
    else:
        raise ValueError(solid)
    normals = ConvexHull(vertices).equations[:, :3]
    return np.unique(np.round(normals, 12), axis=0)


def make_mesh(solid, samples=5600, segments=48, rings=32):
    sites = face_centers(solid)
    count = len(sites)
    separation = np.arccos(np.clip(sites @ sites.T, -1, 1)) + np.eye(count)*10
    b = min(1.12, .84*separation.min())
    tau = .42*b
    umax = math.acosh(b/tau)
    half_gap = .65*tau*umax
    theta = np.linspace(0, 2*math.pi, segments, endpoint=False)

    def directions(n, t):
        # A stable frame, including necks on the vertical coordinate axis.
        axis = np.eye(3)[np.argmin(np.abs(n))]
        e1 = np.cross(axis, n); e1 /= np.linalg.norm(e1)
        e2 = np.cross(n, e1)
        tangent = np.cos(theta)[:, None]*e1 + np.sin(theta)[:, None]*e2
        return math.cos(t/2)*n + math.sin(t/2)*tangent

    k = np.arange(samples); z = 1-2*(k+.5)/samples
    angle = k*math.pi*(3-math.sqrt(5))
    q = np.column_stack([np.sqrt(1-z*z)*np.cos(angle), np.sqrt(1-z*z)*np.sin(angle), z])
    q = q[np.max(q @ sites.T, axis=1) < math.cos(b/2+.02)]
    boundaries = []
    for n in sites:
        boundaries.append(np.arange(len(q), len(q)+segments))
        q = np.vstack([q, directions(n, b)])
    faces = ConvexHull(q).simplices
    faces = faces[np.max(q[faces].mean(axis=1) @ sites.T, axis=1) < math.cos(b/2)-1e-10]
    nq = len(q)
    vertices = np.vstack([(2+half_gap)*q, (2-half_gap)*q]).tolist()
    result = np.vstack([faces, faces+nq]).tolist()
    face_groups = [0]*len(faces) + [1]*len(faces)
    vertex_groups = [0]*nq + [1]*nq
    for n, boundary in zip(sites, boundaries):
        loops = [boundary+nq]
        for u in np.linspace(-umax, umax, rings+1)[1:-1]:
            t = tau*math.cosh(u)
            w = np.clip((t-.65*b)/(.35*b), 0, 1)
            blend = w**3*(10-15*w+6*w*w)
            height = (1-blend)*.65*tau*abs(u) + blend*half_gap
            p = (2+math.copysign(height, u))*directions(n, t)
            loops.append(np.arange(len(vertices), len(vertices)+segments))
            vertices.extend(p.tolist()); vertex_groups.extend([2]*segments)
        loops.append(boundary)
        for lower, upper in zip(loops, loops[1:]):
            for i in range(segments):
                j = (i+1) % segments
                result.extend([[lower[i], lower[j], upper[j]], [lower[i], upper[j], upper[i]]])
                face_groups.extend([2, 2])
    vertices = np.array(vertices)
    faces, normals, audit = orient_and_audit(vertices, np.array(result))
    assert audit['genus'] == count-1
    assert len(vertices) < 65536
    assert b < separation.min()
    audit.update(necks=count, minimum_site_angle=float(separation.min()),
                 patch_radius=float(b), waist_parameter=float(tau), half_gap=float(half_gap))
    data = dict(name='ketover-platonic', kind='platonic-doubling-schematic', status='schematic',
                solid=solid, necks=count, genus=count-1,
                vertices=np.round(vertices, 7).tolist(), normals=np.round(normals, 7).tolist(),
                faces=faces.tolist(), paths=[], faceGroups=face_groups, vertexGroups=vertex_groups,
                palette=COLORS.tolist(), sites=np.round(2*sites, 9).tolist(),
                view=dict(yaw=.55, pitch=.33, radius=2.85),
                construction=dict(base_radius=2, patch_radius=b, waist_parameter=tau,
                                  half_gap=half_gap, radial_compression=.65,
                                  segments=segments, rings=rings),
                description='Two punctured spherical sheets joined through face-center necks. '
                'Original compact sweepout schematic, not a computed self-shrinker. '
                'Compactness and ends of the min-max limit are not determined by this drawing.')
    return data, audit


def render_mesh(data, width=560, cut=False):
    """Depth-sorted triangles, supersampled for the static SVG fallback."""
    vertices = np.array(data['vertices']); faces = np.array(data['faces'])
    yaw, pitch = .55, .33
    x, y, z = vertices.T
    a = x*np.cos(yaw)-y*np.sin(yaw); b = x*np.sin(yaw)+y*np.cos(yaw)
    q = np.column_stack([a, z*np.cos(pitch)-b*np.sin(pitch), z*np.sin(pitch)+b*np.cos(pitch)])
    xy = np.column_stack([width/2+width*.18*q[:, 0], width/2-width*.18*q[:, 1]])
    surface = Image.new('RGBA', (width*3, width*3))
    painter = ImageDraw.Draw(surface)
    for j in np.argsort(q[faces, 2].mean(axis=1)):
        f = faces[j]; a, b, c = q[f]
        n = np.cross(b-a, c-a); n /= np.linalg.norm(n)
        if n[2] < 0: n = -n
        light = .48+.50*max(0, n @ np.array([-.35, .55, .76]))
        rgb = np.rint(COLORS[data['faceGroups'][j]]*light).astype(int)
        polygon = list(xy[f])
        if cut:
            polygon = []
            for ia, ib in zip(f, np.roll(f, -1)):
                ya, yb = vertices[ia, 1], vertices[ib, 1]
                if ya <= 0: polygon.append(xy[ia])
                if (ya <= 0) != (yb <= 0): polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
            if len(polygon) < 3: continue
        painter.polygon([(round(3*p[0]), round(3*p[1])) for p in polygon],
                        fill=tuple(int(v) for v in rgb)+(255,))
    return surface.resize((width*2, width*2), Image.Resampling.LANCZOS)


def drawing(models):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 960" role="img" aria-labelledby="title desc">',
             '<title id="title">Ketover Platonic doubling: connected sheets and face-center necks</title>',
             '<desc id="desc">A full surface and cutaway show the cube sweepout model with six radial necks and genus five. '
             'Five smaller models compare tetrahedral, cubical, octahedral, dodecahedral and icosahedral face-center arrangements. '
             'Original construction schematic, not computed self-shrinkers. Compactness of the min-max limits is not proved.</desc>',
             '<rect width="1200" height="960" fill="#f7fafb"/>',
             '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
             '<text x="40" y="49" font-size="30" font-weight="600">Ketover’s Platonic shrinkers</text>',
             '<text x="40" y="82" font-size="20" fill="#58727e">Construction picture: two spherical sheets joined at face centers</text>']

    def picture(data, x, y, size, cut=False):
        buffer = io.BytesIO(); render_mesh(data, size, cut).save(buffer, format='PNG', optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
        parts.append(f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/png;base64,{encoded}"/>')

    picture(models['cube'], 70, 100, 460)
    picture(models['cube'], 670, 100, 460, True)
    for x, title, subtitle in [(300, 'Doubled cube · 6 necks · genus 5', 'One connected surface'),
                                (900, 'Cutaway reveals the inner sheet', 'Cut edges are a viewing aid')]:
        parts.extend([f'<text x="{x}" y="548" text-anchor="middle" font-size="22" font-weight="600">{title}</text>',
                      f'<text x="{x}" y="577" text-anchor="middle" font-size="18" fill="#58727e">{subtitle}</text>'])
    for x, name, color in [(270, 'Outer sheet', '#4b8ba3'), (500, 'Inner sheet', '#d3a963'), (730, 'Connecting necks', '#bc744d')]:
        parts.append(f'<circle cx="{x}" cy="613" r="6" fill="{color}"/><text x="{x+16}" y="619" font-size="18">{name}</text>')
    parts.append('<path d="M40 644H1160" stroke="#cedde3"/>')
    for i, (solid, count, group) in enumerate(SOLIDS):
        cx = 130+235*i
        picture(models[solid], cx-76, 657, 152)
        parts.append(f'<text x="{cx}" y="826" text-anchor="middle" font-size="18" font-weight="600">{solid.capitalize()}</text>')
        parts.append(f'<text x="{cx}" y="853" text-anchor="middle" font-size="17">{count} necks · genus {count-1}</text>')
    parts += ['<path d="M40 875H1160" stroke="#cedde3"/>',
              '<text x="40" y="910" font-size="19" font-weight="600">SCHEMATIC · not a numerical solution of the shrinker equation</text>',
              '<text x="40" y="939" font-size="18" fill="#58727e">The models are compact; compactness and ends of Ketover’s min-max limits remain undetermined.</text>',
              '</g></svg>']
    (OUT/'ketover-platonic.svg').write_text('\n'.join(parts)+'\n')


def main():
    models, audits = {}, {}
    for solid, count, group in SOLIDS:
        data, audits[solid] = make_mesh(solid)
        assert data['necks'] == count
        data['rotation_group'] = group
        models[solid] = data
        name = 'ketover-platonic' + ('' if solid == 'cube' else '-'+solid)
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
    drawing(models)
    audit = dict(status='schematic', source='https://arxiv.org/pdf/1602.07271v1',
                 source_locations='Theorem 0.1 and introduction, pp. 2–3; Section 2, pp. 9–10; Remark 2.5, pp. 14–15',
                 models=audits)
    (OUT/'platonic-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
