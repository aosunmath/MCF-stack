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
    svg=canvas('Immortal compact product-manifold flow and its double-sphere limit',
        'Generating-profile schematics in polar coordinate x and product coordinate y '
        'for a flow in the round product S^n times R. At finite time a closed loop '
        'avoids both polar axes, giving topology S^1 times S^(n-1). At infinite '
        'time its two necks reach the poles and two sheets approach the same '
        'minimal sphere. This is intrinsic manifold MCF, not Euclidean MCF.')
    text(svg,24,33,'A compact immortal flow in Sⁿ × ℝ',23,650)
    text(svg,24,59,'n ≥ 2 · Generating profiles, shown schematically',fill=MUTED)
    card(svg,20,79,290,251)
    card(svg,330,79,290,251)
    text(svg,36,108,'Finite positive time',18,650)
    text(svg,36,134,'Closed loop away from the poles',15,fill=MUTED)
    text(svg,346,108,'t → ∞',20,650)
    text(svg,346,134,'Two necks collapse at the poles',15,fill=MUTED)
    for left,right in [(52,280),(362,590)]:
        line(svg,left,158,left,267,stroke=BORDER,width=1.5,stroke_dasharray='4 4')
        line(svg,right,158,right,267,stroke=BORDER,width=1.5,stroke_dasharray='4 4')
        line(svg,left,212,right,212,stroke=BORDER,width=1.5,stroke_dasharray='4 4')
        text(svg,left,290,'x = 0',15,anchor='middle')
        text(svg,right,290,'x = π',15,anchor='middle')
        text(svg,left+8,315,'north pole',15,anchor='middle',fill=MUTED)
        text(svg,right-8,315,'south pole',15,anchor='middle',fill=MUTED)
    el(svg,'ellipse',cx=166,cy=212,rx=86,ry=48,fill=PALE,
       stroke=ACCENT,stroke_width=3)
    for x in [80,252]:
        el(svg,'circle',cx=x,cy=212,r=4,fill=INK)
    text(svg,166,218,'profile loop',15,anchor='middle',fill=INK)
    # A single limiting segment represents both coincident sheets.
    line(svg,362,212,590,212,width=5)
    for x in [362,590]:
        el(svg,'circle',cx=x,cy=212,r=5,fill=INK)
    line(svg,407,185,365,205,width=1.4,marker_end='url(#arrow)')
    line(svg,545,185,587,205,width=1.4,marker_end='url(#arrow)')
    text(svg,476,182,'neck limits',15,anchor='middle')
    text(svg,476,244,'2 · (Sⁿ × {0})',18,650,anchor='middle')
    text(svg,476,268,'one slice, multiplicity two',15,anchor='middle',fill=MUTED)
    text(svg,24,359,'Finite-time topology: S¹ × Sⁿ⁻¹; genus 1 when n = 2, with no ends.',15)
    text(svg,24,388,'Intrinsic product-manifold flow. This drawing is not Euclidean MCF.',15,fill=MUTED)
    save('immortal-product.svg',svg)


if __name__=='__main__':
    immortal_annulus()
    immortal_product()
