#!/usr/bin/env python3
"""Original schematic diagrams for the Chen–Sun immortal constructions.

Run: python3 scripts/generate_immortal_flow_schematics.py

These are illustrative geometry, not computed solutions of the critical PDE.
The annulus uses the shared JavaScript stage model. Its interpolated shapes
illustrate qualitative convergence without assigning physical times.
"""
from __future__ import annotations
import math
from pathlib import Path
from xml.etree import ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
OUT = Path(__file__).resolve().parents[1] / 'site' / 'assets' / 'solitons'
BG, ACCENT, INK, MUTED = '#f7fafb', '#21667f', '#183f52', '#526b77'
BORDER, PALE = '#d3e2e8', '#e5f1f5'


def el(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{NS}}}{tag}',
        {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def text(parent, x, y, value, size=15, weight=400, anchor='start', fill=INK):
    el(parent, 'text', x=x, y=y, fill=fill, font_size=size,
       font_weight=weight, text_anchor=anchor).text = value


def path(parent, d, stroke=ACCENT, width=2, fill='none', **attrs):
    return el(parent, 'path', d=d, stroke=stroke, stroke_width=width,
              fill=fill, stroke_linecap='round', stroke_linejoin='round', **attrs)


def line(parent, x1, y1, x2, y2, **attrs):
    return path(parent, f'M{x1},{y1} L{x2},{y2}', **attrs)


def curve(parent, points, **attrs):
    return path(parent, 'M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in points), **attrs)


def card(parent, x, y, w, h):
    el(parent, 'rect', x=x, y=y, width=w, height=h, rx=12,
       fill='#ffffff', stroke=BORDER, stroke_width=1)


def canvas(title, description):
    svg = ET.Element(f'{{{NS}}}svg', {
        'width':'640', 'height':'410', 'viewBox':'0 0 640 410',
        'role':'img', 'aria-labelledby':'title description',
        'font-family':'system-ui, -apple-system, Segoe UI, sans-serif',
    })
    el(svg, 'title', id='title').text=title
    el(svg, 'desc', id='description').text=description
    el(svg, 'rect', width=640, height=410, fill=BG)
    defs=el(svg,'defs')
    arrow=el(defs,'marker',id='arrow',viewBox='0 0 10 10',refX=8,refY=5,
             markerWidth=5,markerHeight=5,orient='auto-start-reverse')
    path(arrow,'M0,0 L10,5 L0,10 Z',width=0,fill=ACCENT)
    return svg


def save(name, svg):
    OUT.mkdir(parents=True, exist_ok=True)
    ET.indent(svg)
    ET.ElementTree(svg).write(OUT/name, encoding='utf-8', xml_declaration=True)
    ET.parse(OUT/name)
    print((OUT/name).relative_to(OUT.parents[2]))


def immortal_annulus():
    # Shared JS geometry keeps the static and interactive stages consistent.
    import subprocess
    subprocess.run(['node', str(Path(__file__).with_name('generate_immortal_annulus.mjs'))], check=True)


def immortal_product():
    # Keep the legacy regeneration entry point; the viewer and SVG now share a model.
    import subprocess
    subprocess.run(['node', str(Path(__file__).with_name('generate_immortal_product.mjs'))],
                   check=True)


if __name__=='__main__':
    immortal_annulus()
    immortal_product()
