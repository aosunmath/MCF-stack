#!/usr/bin/env python3
"""Original schematic sections of Mramor–Yudowitz, arXiv:2509.26515v3.

Theorem 1.1, Figure 1, §2.2 and §3.1 inform the drawing. These Bezier
arcs encode the qualitative profile, not a numerical solution of (2.6).
Run with Python's standard library; no source-paper artwork is copied.
"""
import json
import math
from collections import Counter
from pathlib import Path

from generate_expander_schematics import canvas, text, path, curve, line, el, save

OUT = Path(__file__).resolve().parents[1] / 'site/assets/solitons'
BLUE, COPPER, MUTED = '#21667f', '#b66a35', '#526b77'
SEGMENTS, STEPS = 72, 24
PHASE = math.pi / 2 + .15


def profile():
    # z decreases strictly: a radius graph over the axis, with a smooth
    # horizontal tangent at the pole and vertical tangents at rim and neck.
    arcs = [
        [(0, 1.5), (1.9, 1.5), (4.6, 1.48), (4.6, .98)],
        [(4.6, .98), (4.6, .48), (1.22, .46), (.78, .32)],
        [(.78, .32), (.58, .32 - .2 * .14 / .44), (.48, .16), (.48, 0)],
    ]
    upper = []
    for arc in arcs:
        for i in range(STEPS):
            t = i / STEPS
            w = [(1-t)**3, 3*t*(1-t)**2, 3*t*t*(1-t), t**3]
            upper.append([sum(w[k]*arc[k][j] for k in range(4)) for j in range(2)])
    upper.append([.48, 0])
    return upper + [[r, -z] for r, z in upper[-2::-1]]


def geometry(p):
    vertices, rings = [], []
    for r, z in p:
        if r == 0:
            rings.append([len(vertices)]); vertices.append([0, 0, z])
        else:
            rings.append(list(range(len(vertices), len(vertices)+SEGMENTS)))
            vertices.extend([[r*math.cos(PHASE+2*math.pi*j/SEGMENTS),
                              r*math.sin(PHASE+2*math.pi*j/SEGMENTS), z]
                             for j in range(SEGMENTS)])
    faces, sectors, groups = [], [], []
    for i, (a, b) in enumerate(zip(rings, rings[1:])):
        for j in range(SEGMENTS):
            k = (j+1) % SEGMENTS
            if len(a) == 1:
                pair = [[a[0], b[j], b[k]]]
            elif len(b) == 1:
                pair = [[a[j], b[0], a[k]]]
            else:
                pair = [[a[j], b[j], b[k]], [a[j], b[k], a[k]]]
            faces.extend(pair); sectors.extend([j]*len(pair))
            groups.extend([int(abs((p[i][1]+p[i+1][1])/2) < .32)]*len(pair))
    # Independent combinatorial checks: the complete section is a sphere,
    # without a spurious hole or pinched pole. The cutaway is display only.
    edges = Counter(tuple(sorted((f[j], f[(j+1) % 3]))) for f in faces for j in range(3))
    assert set(edges.values()) == {2}
    assert len(vertices)-len(edges)+len(faces) == 2
    assert all(a[1] > b[1] for a, b in zip(p, p[1:]))
    extrema = [i for i in range(1, len(p)-1)
               if (p[i][0]-p[i-1][0])*(p[i+1][0]-p[i][0]) < 0]
    assert len(extrema) == 3 and extrema[1] == len(p)//2
    return dict(name='stacked-pancakes', status='schematic',
        description='Schematic 3D linear section of a rotational hypersurface in R^(n+1), n >= 3; not an R3 mean curvature flow.',
        viewLabel='Schematic 3D section · ambient dimension ≥ 4',
        vertices=vertices, faces=faces, paths=[], faceGroups=groups,
        palette=[[67,139,169], [190,119,67]], view={'pitch': .16, 'radius': 3.25, 'horizontalRadius': 4.6, 'seamWidth': 1},
        revolution=dict(segments=SEGMENTS, degrees=270, faceSectors=sectors, meridian=p,
            meridianLabel='Schematic meridian · ambient dimension ≥ 4',
            surfaceHelp='Schematic 3D section, not an R3 flow. Drag to rotate; + / − zoom. Revolve to 360° to close the display cutaway. Copper marks the neck; Meridian shows the radius profile.',
            meridianHelp='Schematic radius profile: blue upper half, orange reflected lower half. Two radius maxima and one positive neck minimum. Height z is the paper’s axial x coordinate; no flow is numerically solved.'),
        source={'url': 'https://arxiv.org/abs/2509.26515v3',
                'locators': ['Theorem 1.1', 'Figure 1', 'Section 2.2, equation (2.6)', 'Section 3.1']})


def rotate(v):
    x, y, z = v
    h = x*math.cos(.64)-y*math.sin(.64)
    d = x*math.sin(.64)+y*math.cos(.64)
    return h, z*math.cos(.16)-d*math.sin(.16), z*math.sin(.16)+d*math.cos(.16)


def surface_drawing(data):
    s = canvas('Two pancakes, one connecting neck', data['description'])
    text(s, 24, 33, 'Two pancakes, one connecting neck', 22, weight=650)
    text(s, 24, 59, 'Schematic 3D section · ambient dimension ≥ 4', 15, fill=MUTED)
    q = [rotate(v) for v in data['vertices']]
    screen = lambda v: (320+57*v[0], 211-57*v[1])
    selected = [i for i, j in enumerate(data['revolution']['faceSectors']) if j < 54]
    for i in sorted(selected, key=lambda i: sum(q[j][2] for j in data['faces'][i])):
        a, b, c = [q[j] for j in data['faces'][i]]
        u, v = [b[k]-a[k] for k in range(3)], [c[k]-a[k] for k in range(3)]
        n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        light = .42+.52*abs(sum(x*y for x, y in zip(n, [.3, .5, .8]))/(math.hypot(*n) or 1))
        rgb = [round(base*light+255*(1-light)*.25) for base in data['palette'][data['faceGroups'][i]]]
        color = 'rgb('+','.join(map(str, rgb))+')'
        el(s, 'polygon', points=' '.join(f'{x:.2f},{y:.2f}' for x, y in map(screen, [a,b,c])),
           fill=color, stroke=color, stroke_width='1.0', stroke_linejoin='round')
    line(s, 341, 216, 443, 227, stroke=COPPER, width=1.4)
    text(s, 448, 232, 'one neck', 16, fill=COPPER)
    text(s, 24, 355, 'A quarter is removed to reveal the connection.', 16)
    text(s, 24, 381, 'The full hypersurface has Sⁿ topology, n ≥ 3.', 15, fill=MUTED)
    save('stacked-pancakes.svg', s)


def profile_drawing(p):
    s = canvas('Meridian: two maxima and one neck',
        'An original qualitative meridian with two radius maxima, one positive neck minimum, two poles, a reflection plane and fixed slab boundaries. Not to scale.')
    text(s, 24, 33, 'Meridian: two maxima and one neck', 22, weight=650)
    text(s, 24, 59, 'Schematic · r = |y|, y ∈ ℝⁿ · axial coordinate x', 15, fill=MUTED)
    xy = lambda r, z: (255+49*r, 211-57*z)
    # Fixed containing slab, separate from the two moving caps.
    for z in [-1.83, 1.83]:
        line(s, 24, xy(0,z)[1], 605, xy(0,z)[1], stroke='#a5bbc6', width=1.2, stroke_dasharray='6 5')
    text(s, 29, 98, 'fixed slab boundary', 13, fill=MUTED)
    text(s, 29, 334, 'fixed slab boundary', 13, fill=MUTED)
    outline = [xy(r,z) for r,z in p]+[xy(-r,z) for r,z in reversed(p)]
    curve(s, outline+[outline[0]], fill='#e1eef3', stroke='#a2bac6', width=1.2)
    line(s, 255, 85, 255, 327, stroke=MUTED, width=1, stroke_dasharray='4 4')
    line(s, 28, 211, 603, 211, stroke=MUTED, width=1, stroke_dasharray='4 4')
    text(s, 265, 88, 'x', 16)
    text(s, 29, 202, 'x = 0', 14, fill=MUTED)
    text(s, 29, 229, 'reflection plane', 13, fill=MUTED)
    curve(s, [xy(r,z) for r,z in p], stroke=BLUE, width=3)
    curve(s, [xy(r,z) for r,z in p if abs(z) <= .32], stroke=COPPER, width=3.5)
    for z in [.98, -.98]:
        x, y = xy(4.6,z)
        el(s, 'circle', cx=x, cy=y, r=4.2, fill=BLUE)
        line(s, x+7, y, 499, y, stroke=BLUE, width=1)
        text(s, 503, y+5, 'maximum', 14, fill=BLUE)
    x,y = xy(.48,0)
    el(s, 'circle', cx=x, cy=y, r=4.2, fill=COPPER)
    line(s, x+6, y, 331, y, stroke=COPPER, width=1)
    el(s, 'rect', x=332, y=198, width=112, height=25, fill='#f7fafb')
    text(s, 337, 216, 'neck minimum', 14, fill=COPPER)
    for z in [1.5,-1.5]:
        x,y=xy(0,z);el(s,'circle',cx=x,cy=y,r=3,fill=BLUE)
    text(s, 160, 117, 'axis / poles', 13, fill=MUTED)
    line(s, 236, 119, 252, 124, stroke=MUTED, width=1)
    line(s, 255, 302, 365, 302, stroke=BLUE, width=1.3, marker_end='url(#arrow)')
    text(s, 373, 307, 'radius r', 14, fill=BLUE)
    text(s, 24, 365, 'Off the poles, each profile point represents an Sⁿ⁻¹ orbit.', 15)
    text(s, 24, 389, 'Proportions are illustrative; no time slice is computed.', 14, fill=MUTED)
    save('stacked-pancakes-profile.svg', s)


def main():
    p = profile(); data = geometry(p)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'stacked-pancakes.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
    surface_drawing(data); profile_drawing(p)
    print('Generated schematic 3D section and meridian; radius graph and sphere mesh checked.')


if __name__ == '__main__':
    main()
