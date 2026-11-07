#!/usr/bin/env python3
"""Generate original, source-conscious SVG diagrams for the MCF catalogue.

The cone is schematic. The network uses its dedicated numerical ODE generator;
the neckpinch delegates to its asymptotic time-sequence renderer, whose compact
slices are schematic and whose bowl cap is numerical. No source-paper figure
or private PDF asset is copied.

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
    # Keep the old entry point from overwriting the solved network with a sketch.
    from generate_expanding_network import main as generate_network
    generate_network()


def neckpinch_scales():
    # Retain the public filename, using the source-based time-sequence renderer.
    import subprocess
    subprocess.run(['node', str(ROOT / 'scripts/render_neckpinch_picture.mjs')], check=True)


def main():
    mean_convex_cone()
    expanding_network()
    neckpinch_scales()
    for name in ['mean-convex-cone.svg','expanding-network.svg','neckpinch-scales.svg']:
        ET.parse(OUT / name)
        print((OUT / name).relative_to(ROOT))


if __name__ == '__main__':
    main()
