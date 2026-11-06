"""Original Møller limiting-configuration illustration; Python standard library.

Uses the committed numerical Angenent meridian, not a circular torus. No
finite-genus desingularized shrinker is computed. Read the source and audit
notes in documentation/moller-picture.md before changing this model.
"""
from html import escape
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
PALETTE = [[221, 171, 101], [67, 139, 169]]
COLORS = ['#b57a2b', '#21667f']
SEAM = '#b34838'


def profile_and_intersections():
    # Import lazily: the older schematic entry point delegates to this module.
    from generate_shrinker_schematics import recover_rotational_profile, sphere_profile_intersections
    torus = json.loads((OUT / 'angenent-torus.json').read_text())
    profile = recover_rotational_profile(torus)
    return profile, sphere_profile_intersections(profile)


def geometry():
    profile, intersections = profile_and_intersections()
    vertices, faces, groups, sectors = [], [], [], []
    segments = 64

    def revolve(curve, group):
        start = len(vertices)
        for z, r in curve:
            vertices.extend([[r*math.cos(2*math.pi*j/segments), r*math.sin(2*math.pi*j/segments), z]
                             for j in range(segments)])
        for i in range(len(curve)-1):
            for j in range(segments):
                a, b = start+i*segments+j, start+i*segments+(j+1)%segments
                faces.extend([[a, a+segments, b+segments], [a, b+segments, b]])
                groups.extend([group, group]); sectors.extend([j, j])

    # Insert the intersection latitude into both meshes. The displayed seam
    # lies on their common polygonal ring instead of crossing coarse faces.
    sphere_z = sorted(set([2*math.cos(math.pi*i/48) for i in range(49)] + [z for z, _ in intersections]))
    sphere = [(z, math.sqrt(max(0, 4-z*z))) for z in sphere_z]
    revolve(sphere, 0)
    torus_mesh = []
    for i, (a, b) in enumerate(zip(profile, profile[1:])):
        if i % 2 == 0:
            torus_mesh.append(a)
        for point in intersections:
            if abs(math.dist(a, point)+math.dist(point, b)-math.dist(a, b)) < 1e-9:
                # Keep the adjacent samples even when decimating the rest.
                if not torus_mesh or torus_mesh[-1] != a:
                    torus_mesh.append(a)
                torus_mesh.extend([point, b])
    torus_mesh.append(profile[-1])
    torus_mesh = [p for i, p in enumerate(torus_mesh) if i == 0 or math.dist(p, torus_mesh[i-1]) > 1e-10]
    revolve(torus_mesh, 1)
    paths = []
    for z, r in intersections:
        start = len(vertices)
        vertices.extend([[r*math.cos(2*math.pi*j/segments), r*math.sin(2*math.pi*j/segments), z]
                         for j in range(segments)])
        paths.append(list(range(start, start+segments)) + [start])
    return {
        'name': 'moller-gluing', 'kind': 'moller-configuration',
        'status': 'numerical-limiting-configuration',
        'description': 'Møller limiting sphere–torus configuration before desingularization; not a smooth high-genus shrinker.',
        'vertices': [[round(x, 8) for x in p] for p in vertices],
        'faces': faces, 'faceGroups': groups, 'faceSectors': sectors,
        'segments': segments, 'paths': paths, 'palette': PALETTE,
        'meridians': [[[r, z] for z, r in sphere], [[r, z] for z, r in profile]],
        'intersections': [{'z': z, 'r': r} for z, r in intersections],
        'view': {'yaw': .64, 'pitch': .22, 'degrees': 360, 'radius': 3.4},
        'source': {'url': 'https://arxiv.org/abs/1111.7318v2',
                   'locators': 'Theorem 1; Figures 1–2; Proposition 2.1; Lemma 2.6'},
        'normalization': 'Hvec = -Xperp/2; sphere radius 2',
        'limitations': 'The torus is a numerical ODE model. Cut edges are display boundaries. Intersection rings are drawn through surfaces for orientation. No handles or genus parameter are modeled.',
    }


def project(p, yaw=.64, pitch=.22):
    x, y, z = p
    depth = x*math.sin(yaw)+y*math.cos(yaw)
    return [x*math.cos(yaw)-y*math.sin(yaw), z*math.cos(pitch)-depth*math.sin(pitch),
            z*math.sin(pitch)+depth*math.cos(pitch)]


def static_svg(data):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title description">',
             '<title id="title">Møller’s sphere–torus gluing configuration</title>',
             '<desc id="description">A shaded view of the radius-two sphere and numerical Angenent torus, with both intersection circles in red. The right panel shows their meridians. This is the singular input before handle insertion, not a computed high-genus shrinker.</desc>',
             '<rect width="640" height="410" fill="#f7fafb"/>',
             '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52" stroke-linejoin="round">']

    def text(x, y, value, size=14, **attributes):
        extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attributes.items())
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" {extra}>{escape(value)}</text>')

    def path(points, color, width=2, extra=''):
        pts = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>')

    text(24, 32, 'Møller’s sphere–torus construction', 22, font_weight=600)
    text(24, 56, 'Singular limit before handle insertion', 15, fill='#617785')
    text(24, 88, 'Limiting configuration', 14, font_weight=600)
    text(415, 88, 'Meridian (r, z)', 14, font_weight=600)
    q = [project(p) for p in data['vertices']]
    screen = lambda p: (202+53*p[0], 207-53*p[1])
    visible = range(len(data['faces']))
    for i in sorted(visible, key=lambda i: sum(q[j][2] for j in data['faces'][i])/3):
        a, b, c = [q[j] for j in data['faces'][i]]
        u, v = [b[k]-a[k] for k in range(3)], [c[k]-a[k] for k in range(3)]
        n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        light = .42+.52*abs(sum(n[k]*[.3,.5,.8][k] for k in range(3))/(math.hypot(*n) or 1))
        rgb = ','.join(str(round(x*light+255*(1-light)*.25)) for x in PALETTE[data['faceGroups'][i]])
        coords = ' '.join(f'{x:.2f},{y:.2f}' for x, y in map(screen, [a,b,c]))
        parts.append(f'<polygon points="{coords}" fill="rgb({rgb})" stroke="rgb({rgb})" stroke-width=".35"/>')
    for ring in data['paths']:
        # The circles are intentionally overlaid, including the cut sector.
        path([screen(q[j]) for j in ring], SEAM, 1.7, 'stroke-dasharray="4 2"')
    parts.append('<path d="M396 108V306" stroke="#d3dfe4"/>')
    plane = lambda p: (428+49*p[0], 207-49*p[1])
    for a, b in [([0,-2.2],[0,2.2]), ([0,0],[3.6,0])]:
        path([plane(a),plane(b)], '#9aaeb7', 1, 'stroke-dasharray="3 3"')
    for meridian, color in zip(data['meridians'], COLORS):
        path([plane(p) for p in meridian], color, 2.4)
    for point in data['intersections']:
        x,y = plane([point['r'],point['z']])
        parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{SEAM}" stroke="#fff"/>')
    text(609, 225, 'r', 13); text(416, 104, 'z', 13)
    text(24, 326, 'Sphere: radius 2', 14, fill=COLORS[0])
    text(214, 326, 'Torus: numerical ODE', 14, fill=COLORS[1])
    text(430, 326, 'Two intersection circles', 14, fill=SEAM)
    text(24, 355, 'Red circles are overlaid through the surfaces.', 14)
    text(24, 380, 'No finite-genus shrinker is computed. See Møller, Figures 1–2.', 14, fill='#617785')
    parts.append('</g></svg>')
    return '\n'.join(parts)+'\n'


def main():
    data = geometry()
    (OUT/'moller-gluing.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n')
    (OUT/'moller-gluing.svg').write_text(static_svg(data))
    print('Generated Møller limiting configuration, meridian and interactive geometry.')
    print('Numerical intersections:', data['intersections'])


if __name__ == '__main__':
    main()
