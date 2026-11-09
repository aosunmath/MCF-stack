"""Original models of Ketover's Platonic doubling sweepouts, not shrinkers.

Requires NumPy and Pillow. No source images or numerical shrinker meshes are
used. See documentation/platonic-picture.md for the construction.
"""
from collections import defaultdict, deque
from itertools import combinations, product
from pathlib import Path
import base64
import io
import json
import math

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
SOLIDS = [('tetrahedron', 4, 'T12'), ('cube', 6, 'O24'),
          ('octahedron', 8, 'O24'), ('dodecahedron', 12, 'I60'),
          ('icosahedron', 20, 'I60')]
COLORS = np.array([[75, 139, 163], [211, 169, 99], [188, 116, 77]])
RADIUS, HALF_GAP = 2., .28


def unit(p):
    return p / np.linalg.norm(p, axis=-1, keepdims=True)


def polyhedron(name):
    phi = (1 + math.sqrt(5)) / 2
    if name == 'tetrahedron':
        v = [p for p in product([-1, 1], repeat=3) if math.prod(p) == 1]
    elif name == 'cube':
        v = list(product([-1, 1], repeat=3))
    elif name == 'octahedron':
        v = np.vstack([np.eye(3), -np.eye(3)])
    else:
        v = list(product([-1, 1], repeat=3)) if name == 'dodecahedron' else []
        a, b = (1/phi, phi) if name == 'dodecahedron' else (1, phi)
        for x, y in product([-a, a], [-b, b]):
            v.extend([(0, x, y), (x, y, 0), (y, 0, x)])
    v = unit(np.array(v, dtype=float))
    faces = set()
    # Supporting planes identify whole polygonal faces, including pentagons.
    for a, b, c in combinations(v, 3):
        n = np.cross(b-a, c-a)
        if np.linalg.norm(n) < 1e-8:
            continue
        n = unit(n)
        distances = (v-a) @ n
        if np.min(distances) > -1e-8 or np.max(distances) < 1e-8:
            faces.add(tuple(np.flatnonzero(np.abs(distances) < 1e-8)))
    ordered = []
    for face in sorted(faces):
        n = unit(v[list(face)].mean(axis=0))
        e = unit(v[face[0]] - n*np.dot(n, v[face[0]]))
        f = np.cross(n, e)
        ordered.append(sorted(face, key=lambda i: math.atan2(v[i] @ f, v[i] @ e)))
    return v, ordered


def orient(vertices, faces):
    edges = defaultdict(list)
    for i, f in enumerate(faces):
        for a, b in zip(f, f[1:]+f[:1]):
            edges[tuple(sorted((a, b)))].append((i, 1 if a < b else -1))
    assert all(len(v) == 2 for v in edges.values()), 'Nonmanifold seam'
    adjacent = defaultdict(list)
    for (i, a), (j, b) in edges.values():
        adjacent[i].append((j, -a*b)); adjacent[j].append((i, -a*b))
    signs = {0: 1}; queue = deque([0])
    while queue:
        i = queue.popleft()
        for j, relation in adjacent[i]:
            sign = signs[i]*relation
            if j in signs:
                assert signs[j] == sign, 'Nonorientable mesh'
            else:
                signs[j] = sign; queue.append(j)
    assert len(signs) == len(faces), 'Disconnected mesh'
    faces = np.array([f if signs[i] == 1 else f[::-1] for i, f in enumerate(faces)])
    a, b, c = vertices[faces].transpose(1, 0, 2)
    if np.sum(a*np.cross(b, c)) < 0:
        faces = faces[:, ::-1]
    a, b, c = vertices[faces].transpose(1, 0, 2)
    cross = np.cross(b-a, c-a)
    normals = np.zeros_like(vertices)
    for i in range(3):
        np.add.at(normals, faces[:, i], cross)
    assert np.min(np.linalg.norm(normals, axis=1)) > 1e-10
    return faces, unit(normals), dict(components=1, boundary_edges=0,
        orientable=True, euler_characteristic=len(vertices)-len(edges)+len(faces),
        vertices=len(vertices), faces=len(faces),
        minimum_triangle_area=float(np.linalg.norm(cross, axis=1).min()/2))


def make_mesh(name, count, group, edge_samples=12, sheet_rings=10, neck_rings=20):
    solid, polygons = polyhedron(name)
    assert len(polygons) == count
    vertices, faces, groups, sites, waists = [], [], [], [], []
    opening_angles = []
    lookup = {}

    def vertex(p, color):
        key = tuple(np.round(p, 9))
        if key not in lookup:
            lookup[key] = len(vertices); vertices.append(p); groups.append(color)
        return lookup[key]

    def strip(a, b):
        for j in range(len(a)):
            k = (j+1) % len(a)
            faces.extend([[a[j], a[k], b[k]], [a[j], b[k], b[j]]])

    for polygon in polygons:
        p = solid[polygon]; n = unit(p.mean(axis=0)); sites.append(n)
        edge_midpoints = unit(p + np.roll(p, -1, axis=0))
        inradius = float(np.arccos(np.max(edge_midpoints @ n)))
        alpha = .72*inradius
        opening_angles.append(alpha)
        boundary = unit(np.array([(1-t)*a+t*b for a, b in zip(p, np.roll(p, -1, axis=0))
                                  for t in np.arange(edge_samples)/edge_samples]))
        beta = np.arccos(np.clip(boundary @ n, -1, 1))
        tangent = unit(boundary - (boundary @ n)[:, None]*n)

        def ring(r, angle, color):
            angle = np.broadcast_to(angle, beta.shape)
            points = r*(np.cos(angle)[:, None]*n + np.sin(angle)[:, None]*tangent)
            return [vertex(q, color) for q in points]

        openings = []
        for color, sign in enumerate([1, -1]):
            rings = [ring(RADIUS+sign*HALF_GAP, alpha+(beta-alpha)*t, color)
                     for t in np.linspace(0, 1, sheet_rings+1)]
            for a, b in zip(rings, rings[1:]): strip(a, b)
            openings.append(rings[0])
        # A rounded radial bridge: tangent to both spherical sheets at its rims.
        rings = [openings[0]]
        for j in range(1, neck_rings):
            t = math.pi*j/neck_rings
            rings.append(ring(RADIUS+HALF_GAP*math.cos(t), alpha*(1-.40*math.sin(t)), 2))
        rings.append(openings[1])
        waists.append(rings[neck_rings//2])
        for a, b in zip(rings, rings[1:]): strip(a, b)
    vertices = np.array(vertices)
    faces, normals, audit = orient(vertices, faces)
    assert audit['euler_characteristic'] == 4-2*count, audit
    assert len(vertices) < 65536
    data = dict(name='ketover-platonic', kind='platonic-doubling-schematic',
        status='schematic', solid=name, necks=count, genus=count-1, symmetry=group,
        vertices=np.round(vertices, 7).tolist(), faces=faces.tolist(),
        normals=np.round(normals, 7).tolist(), paths=[], vertexGroups=groups,
        palette=COLORS.tolist(), sites=np.round(RADIUS*np.array(sites), 9).tolist(),
        faceGroups=np.max(np.array(groups)[faces], axis=1).tolist(),
        construction=dict(base_radius=RADIUS, half_gap=HALF_GAP,
            opening_angle=opening_angles[0], segments=len(waists[0]), rings=neck_rings,
            edge_samples=edge_samples, sheet_rings=sheet_rings),
        view=dict(yaw=.63, pitch=.38, radius=2.5),
        description='Compact doubling-sweepout model, not a computed self-shrinker. '
        'Compactness and ends of the min-max shrinker are not determined by the paper.')
    audit.update(genus=count-1, necks=count, edge_incidence=[2],
        minimum_site_angle=float(np.arccos(np.clip(np.array(sites) @ np.array(sites).T - np.eye(count)*3, -1, 1)).min()),
        opening_angle=opening_angles[0], half_gap=HALF_GAP)
    return data, audit


def render(data, size, cut=False):
    """Original rasterization of our mesh, embedded in the accessible SVG."""
    scale = 2
    picture = Image.new('RGB', (size*scale, size*scale), '#f7fafb')
    draw = ImageDraw.Draw(picture)
    yaw, pitch = .63, .38
    cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    rotation = np.array([[cy, -sy, 0], [-sy*sp, -cy*sp, cp], [sy*cp, cy*cp, sp]])
    v, f, normal = np.array(data['vertices']), np.array(data['faces']), np.array(data['normals'])
    q = v @ rotation.T; ns = normal @ rotation.T
    xy = np.column_stack([size*scale/2 + q[:, 0]*size*scale/5.2,
                          size*scale/2 - q[:, 1]*size*scale/5.2])
    tint = COLORS[np.array(data['vertexGroups'])]
    light = unit(np.array([-.35, .55, .8]))
    for j in np.argsort(q[f, 2].mean(axis=1)):
        face = f[j]; polygon = list(xy[face])
        if cut:
            polygon = []
            for a, b in zip(face, np.roll(face, -1)):
                ya, yb = v[a, 1], v[b, 1]
                if ya <= 0: polygon.append(xy[a])
                if (ya <= 0) != (yb <= 0):
                    polygon.append(xy[a]+ya/(ya-yb)*(xy[b]-xy[a]))
            if len(polygon) < 3: continue
        n = unit(ns[face].mean(axis=0))
        if n[2] < 0: n = -n
        shade = .48+.50*max(0, n @ light)
        color = tuple(np.round(tint[face].mean(axis=0)*shade).astype(int))
        draw.polygon([tuple(p) for p in polygon], fill=color)
    return picture.resize((size, size), Image.Resampling.LANCZOS)


def drawing(models):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 760" role="img" aria-labelledby="title desc">',
        '<title id="title">Ketover Platonic doubling: two sheets and face-center necks</title>',
        '<desc id="desc">Original sweepout models for all five Platonic solids. A full genus-five cubical model and a cutaway show two spherical sheets joined by six radial necks. The five models have 4, 6, 8, 12 and 20 necks and genera 3, 5, 7, 11 and 19. These compact comparison surfaces are not computed shrinkers; compactness of the limiting shrinkers is not proved.</desc>',
        '<rect width="1000" height="760" fill="#f7fafb"/>',
        '<g font-family="Arial,sans-serif" fill="#183f52">',
        '<text x="30" y="40" font-size="28" font-weight="600">Two spherical sheets, joined at the face centers</text>',
        '<text x="30" y="70" font-size="18">Ketover’s Platonic doubling construction · original sweepout models</text>']
    def picture(data, x, y, size, cut=False):
        buf = io.BytesIO(); render(data, size*2, cut).save(buf, format='PNG')
        encoded = base64.b64encode(buf.getvalue()).decode()
        parts.append(f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/png;base64,{encoded}"/>')
    picture(models['cube'], 55, 82, 360)
    picture(models['cube'], 560, 82, 360, True)
    for x, title, sub in [(235, 'Cube · 6 necks · genus 5', 'One connected surface'),
                          (740, 'Cutaway', 'Inner sheet and connecting neck walls')]:
        parts.extend([f'<text x="{x}" y="446" text-anchor="middle" font-size="19" font-weight="600">{title}</text>',
                      f'<text x="{x}" y="473" text-anchor="middle" font-size="16">{sub}</text>'])
    for i, (name, count, _) in enumerate(SOLIDS):
        x = 100+200*i; picture(models[name], x-68, 498, 136)
        parts.extend([f'<text x="{x}" y="653" text-anchor="middle" font-size="17">{name.title()}</text>',
                      f'<text x="{x}" y="679" text-anchor="middle" font-size="16">{count} necks · genus {count-1}</text>'])
    parts += ['<text x="30" y="719" font-size="17" font-weight="600">SCHEMATIC · no numerical solution of the shrinker equation</text>',
              '<text x="30" y="746" font-size="16">The compact sweepout does not settle compactness or the ends of the min-max shrinker.</text>', '</g></svg>']
    (OUT/'ketover-platonic.svg').write_text('\n'.join(parts)+'\n')


def main():
    models, audits = {}, {}
    for name, count, group in SOLIDS:
        models[name], audits[name] = make_mesh(name, count, group)
        suffix = '' if name == 'cube' else '-'+name
        (OUT/f'ketover-platonic{suffix}.json').write_text(json.dumps(models[name], separators=(',', ':'))+'\n')
    drawing(models)
    (OUT/'platonic-audit.json').write_text(json.dumps(dict(status='schematic',
        source='https://arxiv.org/pdf/1602.07271v1', source_pages=[2, 3, 9, 10, 12, 14, 15],
        models=audits), indent=2)+'\n')
    print(json.dumps(audits, indent=2))


if __name__ == '__main__': main()
