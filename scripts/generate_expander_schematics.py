#!/usr/bin/env python3
"""Generate original, source-conscious SVG diagrams for the MCF catalogue.

All diagrams are explicitly schematic. The intermediate neckpinch curve is
sampled from the limiting formula for n=2, m=3, K=1; it is not a solution at
finite time. No source-paper figure or private PDF asset is copied.

Run: python3 scripts/generate_expander_schematics.py
"""
from __future__ import annotations
import math
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site' / 'assets' / 'solitons'
BG, ACCENT, INK = '#f7fafb', '#21667f', '#183f52'
MUTED, BORDER, PALE = '#526b77', '#d3e2e8', '#e5f1f5'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def el(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{NS}}}{tag}', {
        key.replace('_', '-'): str(value) for key, value in attrs.items()
    })


def text(parent, x, y, value, size=15, fill=INK, weight=400, anchor='start'):
    node = el(parent, 'text', x=x, y=y, fill=fill, font_size=size,
              font_weight=weight, text_anchor=anchor)
    node.text = value
    return node


def path(parent, d, stroke=ACCENT, width=3, fill='none', **attrs):
    return el(parent, 'path', d=d, stroke=stroke, stroke_width=width,
              fill=fill, stroke_linecap='round', stroke_linejoin='round', **attrs)


def line(parent, x1, y1, x2, y2, **attrs):
    return path(parent, f'M{x1},{y1} L{x2},{y2}', **attrs)


def curve(parent, pts, **attrs):
    return path(parent, 'M'+' L'.join(f'{x:.3f},{y:.3f}' for x, y in pts), **attrs)


def card(parent, x, y, width, height):
    return el(parent, 'rect', x=x, y=y, width=width, height=height, rx=12,
              fill='#ffffff', stroke=BORDER, stroke_width=1)


def canvas(title, description):
    root = ET.Element(f'{{{NS}}}svg', {
        'width': '640', 'height': '410', 'viewBox': '0 0 640 410',
        'role': 'img', 'aria-labelledby': 'title description',
        'font-family': 'system-ui, -apple-system, Segoe UI, sans-serif',
    })
    el(root, 'title', id='title').text = title
    el(root, 'desc', id='description').text = description
    el(root, 'rect', width=640, height=410, fill=BG)
    defs = el(root, 'defs')
    marker = el(defs, 'marker', id='arrow', viewBox='0 0 10 10',
                refX=8, refY=5, markerWidth=6, markerHeight=6, orient='auto-start-reverse')
    path(marker, 'M0,0 L10,5 L0,10 Z', width=0, fill=ACCENT)
    return root


def save(name, svg):
    OUT.mkdir(parents=True, exist_ok=True)
    ET.indent(svg)
    ET.ElementTree(svg).write(OUT / name, encoding='utf-8', xml_declaration=True)


def mean_convex_cone():
    svg = canvas('One-sided cone expanders: a schematic slice',
        'A cone bounds the shaded selected side Omega. Three schematic homothetic '
        'leaves move into Omega as time increases. The drawn curves are not computed '
        'self-expanders and do not assert a universal topology.')
    text(svg, 24, 33, 'One chosen side of a mean-convex cone', 23, weight=650)
    text(svg, 24, 59, 'Schematic slice · curves are not computed self-expanders', fill=MUTED)
    card(svg, 20, 77, 600, 263)
    el(svg, 'polygon', points='66,91 574,91 574,103 320,306 66,103', fill=PALE)
    text(svg, 320, 112, 'chosen side Ω', 19, weight=600, anchor='middle')
    for h, opacity in [(24, 0.5), (58, 0.76), (93, 1)]:
        pts = [(320+x, 306-math.sqrt((0.8*x)**2+h*h))
               for x in [i*1.8-234 for i in range(261)]]
        curve(svg, pts, opacity=opacity, width=3)
    path(svg, 'M66,103 L320,306 L574,103', stroke=MUTED, width=2,
         stroke_dasharray='7 6')
    el(svg, 'circle', cx=320, cy=306, r=4, fill=INK)
    text(svg, 335, 326, 'cone vertex', 15)
    text(svg, 581, 112, 'C', 18, weight=650)
    text(svg, 337, 270, 'M', 18, weight=600)
    text(svg, 337, 235, '√t M', 18, weight=600)
    line(svg, 271, 254, 271, 180, width=2, marker_end='url(#arrow)')
    text(svg, 253, 218, 't', 18, anchor='end')
    text(svg, 24, 369, 'The leaves foliate Ω; the cone is its boundary.', 16)
    text(svg, 24, 394, 'Geometry and topology depend on the prescribed cone.', 15, fill=MUTED)
    save('mean-convex-cone.svg', svg)


def expanding_network():
    svg = canvas('Expanding planar tree: schematic and junction condition',
        'An illustrative four-ended tree has two triple junctions. The branches are '
        'not solutions of the expander equation. An inset shows the exact local '
        '120-degree junction angle condition, rather than a nonstationary network.')
    text(svg, 24, 33, 'Expanding planar tree networks', 23, weight=650)
    text(svg, 24, 59, 'Schematic topology · the curved branches have not been solved', fill=MUTED)
    card(svg, 20, 79, 380, 251)
    card(svg, 415, 79, 205, 251)
    text(svg, 36, 108, 'Four asymptotic ends', 18, weight=600)
    # Curves are chosen to illustrate connectivity; no equation-solving claim.
    for d in ['M160,207 C140,172 120,147 70,133',
              'M160,207 C140,242 120,268 70,282',
              'M280,207 C300,172 320,147 370,133',
              'M280,207 C300,242 320,268 370,282']:
        path(svg, d)
    line(svg, 160, 207, 280, 207)
    for x in [160, 280]:
        el(svg, 'circle', cx=x, cy=207, r=4, fill=INK)
    for a,b,c,d in [(70,133,44,126),(70,282,44,289),
                    (370,133,386,129),(370,282,386,286)]:
        line(svg,a,b,c,d,stroke=MUTED,width=2,stroke_dasharray='4 5')
    text(svg, 36, 313, 'Tree structure, not numerical geometry', 15, fill=MUTED)
    text(svg, 429, 108, 'Junction condition', 17, weight=600)
    cx,cy,r = 516,201,60
    for angle in [-90,30,150]:
        a = math.radians(angle)
        line(svg,cx,cy,cx+r*math.cos(a),cy+r*math.sin(a))
    a1,a2 = math.radians(-90),math.radians(30)
    x1,y1=cx+24*math.cos(a1),cy+24*math.sin(a1)
    x2,y2=cx+24*math.cos(a2),cy+24*math.sin(a2)
    path(svg,f'M{x1},{y1} A24,24 0 0 1 {x2},{y2}',width=1.5)
    el(svg, 'circle', cx=cx, cy=cy, r=4, fill=INK)
    text(svg, 546, 181, '120°', 16)
    text(svg, 432, 283, 'Three tangent rays', 15)
    text(svg, 432, 307, 'with equal angles', 15, fill=MUTED)
    text(svg, 24, 361, 'The curvature equation holds along each open branch.', 16)
    text(svg, 24, 389, 'A junction is not a smooth curve point.', 15, fill=MUTED)
    save('expanding-network.svg', svg)


def neckpinch_scales():
    svg = canvas('Three limits of a degenerate neckpinch',
        'Three panels distinguish the cylindrical parabolic limit, the bowl limit '
        'after rescaling at the tip, and an intermediate anisotropic limiting profile. '
        'The first two drawings are schematic; the third plots r=sqrt(2+x^3), '
        'the limit for n=2, m=3 and K=1. No exact full evolving compact surface is drawn.')
    text(svg, 24, 33, 'Three scales near a degenerate neckpinch', 23, weight=650)
    text(svg, 24, 59, 'Limits of the same type-II singularity · not an exact full flow', fill=MUTED)
    for x in [20,225,430]:
        card(svg,x,79,190,249)
    text(svg,34,108,'Parabolic scale',18,weight=600)
    text(svg,34,132,'at the origin',15,fill=MUTED)
    # Schematic cylinder viewed obliquely, with its exact limiting radius stated.
    el(svg, 'ellipse', cx=62, cy=208, rx=15, ry=40, fill=PALE,
       stroke=ACCENT, stroke_width=2)
    el(svg, 'rect', x=62, y=168, width=105, height=80, fill=PALE)
    line(svg,62,168,167,168,width=2)
    line(svg,62,248,167,248,width=2)
    el(svg, 'ellipse', cx=167, cy=208, rx=15, ry=40, fill='none',
       stroke=ACCENT, stroke_width=2)
    path(svg,'M62,168 A15,40 0 0 1 62,248',width=1.3,stroke_dasharray='4 4')
    text(svg,34,281,'Cylinder limit',16,weight=600)
    text(svg,34,307,'radius √[2(n − 1)]',15,fill=MUTED)
    text(svg,239,108,'Tip scale',18,weight=600)
    text(svg,239,132,'at maximum |A|',15,fill=MUTED)
    # A generic convex profile illustrates the bowl type only. It is not an ODE solution.
    path(svg, 'M388,155 C347,161 282,182 274,207 C282,232 347,253 388,259', width=3)
    line(svg,258,207,398,207,stroke=BORDER,width=1.4,stroke_dasharray='4 4')
    line(svg,292,207,341,207,width=2,marker_end='url(#arrow)')
    el(svg,'circle',cx=274,cy=207,r=4,fill=INK)
    text(svg,239,281,'Translating bowl',16,weight=600)
    text(svg,239,307,'schematic profile',15,fill=MUTED)
    text(svg,444,108,'Intermediate scale',17,weight=600)
    text(svg,444,132,'different axial scaling',15,fill=MUTED)
    xmin,xmax=-(2**(1/3)),1.22
    pts=[]
    for i in range(241):
        x=xmin+(xmax-xmin)*i/240
        r=math.sqrt(max(0,2+x**3))
        pts.append((450+(x-xmin)/(xmax-xmin)*151,208-r*25))
    curve(svg,pts)
    curve(svg,[(x,416-y) for x,y in pts])
    line(svg,446,208,607,208,stroke=BORDER,width=1.4,stroke_dasharray='4 4')
    text(svg,444,281,'r = √(2 + x³)',16,weight=600)
    text(svg,444,307,'n = 2, m = 3, K = 1',15,fill=MUTED)
    text(svg,24,361,'The intermediate curve is an asymptotic limiting profile.',16)
    text(svg,24,389,'No exact compact time-dependent solution is depicted.',15,fill=MUTED)
    save('neckpinch-scales.svg',svg)


def main():
    mean_convex_cone()
    expanding_network()
    neckpinch_scales()
    for name in ['mean-convex-cone.svg','expanding-network.svg','neckpinch-scales.svg']:
        ET.parse(OUT / name)
        print((OUT / name).relative_to(ROOT))


if __name__ == '__main__':
    main()
