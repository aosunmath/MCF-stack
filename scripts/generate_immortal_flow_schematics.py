#!/usr/bin/env python3
"""Original schematic diagrams for the Chen–Sun immortal constructions.

Run: python3 scripts/generate_immortal_flow_schematics.py

These are illustrative geometry, not computed solutions of the critical PDE.
The scalar expression used for the annulus drawing only supplies an attractive
smooth neck and planar ends. No finite-time motion is inferred from it.
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
    svg=canvas('Immortal annulus approaching a plane with multiplicity two',
        'Schematic rotational surface with a positive neck radius and two planar '
        'ends at finite time. The right panel represents its local multiplicity-two '
        'plane limit as time tends to infinity. No finite-time singularity or '
        'computed critical solution is depicted.')
    text(svg,24,33,'An immortal annulus in Euclidean space',23,650)
    text(svg,24,59,'Schematic geometry · no critical PDE solution is plotted',fill=MUTED)
    card(svg,20,79,380,254)
    card(svg,415,79,205,254)
    text(svg,36,108,'Finite positive time',18,650)
    text(svg,431,108,'t → ∞',20,650)
    text(svg,431,134,'Local limit',16,fill=MUTED)
    # This convenient surface is only an original illustration, not the theorem's flow.
    neck, outer, height = 0.62, 3.3, 1.05
    def project(r,theta,z):
        return (205+44*r*math.cos(theta),216+13*r*math.sin(theta)-48*z)
    def point(q,theta,sign):
        r=neck+(outer-neck)*q*q
        z=sign*height*math.sqrt(max(0,1-(neck/r)**2))
        return project(r,theta,z)
    # Subtle, depth-ordered quadrilateral shading clarifies the two sheets.
    faces=[]
    nq,nt=16,48
    for sign in [-1,1]:
        for i in range(nq):
            for j in range(nt):
                q0,q1=i/nq,(i+1)/nq
                t0,t1=2*math.pi*j/nt,2*math.pi*(j+1)/nt
                points=[point(q0,t0,sign),point(q1,t0,sign),
                        point(q1,t1,sign),point(q0,t1,sign)]
                depth=math.sin((t0+t1)/2)*(neck+(outer-neck)*((q0+q1)/2)**2)
                faces.append((sign,depth,points))
    for sign,_,points in sorted(faces,key=lambda f:(f[0],f[1])):
        el(svg,'polygon',points=' '.join(f'{x:.2f},{y:.2f}' for x,y in points),
           fill='#cfe4ec' if sign>0 else '#e3edf1',stroke='none')
    for sign in [-1,1]:
        for j in range(12):
            th=2*math.pi*j/12
            curve(svg,[point(i/70,th,sign) for i in range(71)],
                  stroke='#6d98aa',width=1,opacity=0.72)
        for q in [0,0.42,0.7,1]:
            curve(svg,[point(q,2*math.pi*j/120,sign) for j in range(121)],
                  stroke=ACCENT,width=1.4 if q==0 else 1,opacity=0.85)
    # The finite neck is a circle of positive radius, not a point singularity.
    text(svg,300,208,'neck',15,650)
    line(svg,294,213,234,218,width=1.4,marker_end='url(#arrow)')
    text(svg,36,317,'Truncated view · two planar ends and a neck',15,fill=MUTED)
    # One geometric plane, with multiplicity marked rather than faked separation.
    el(svg,'ellipse',cx=518,cy=209,rx=74,ry=22,fill=PALE,
       stroke=ACCENT,stroke_width=2.5)
    line(svg,449,204,586,214,stroke='#9ebfcd',width=1)
    line(svg,484,192,551,227,stroke='#9ebfcd',width=1)
    text(svg,518,258,'multiplicity 2',18,650,anchor='middle')
    text(svg,518,285,'one plane counted twice',15,anchor='middle',fill=MUTED)
    text(svg,24,362,'The neck collapses only at infinite time.',16)
    text(svg,24,390,'The two ends keep their fixed asymptotic planes; convergence is local.',15,fill=MUTED)
    save('immortal-annulus.svg',svg)


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
