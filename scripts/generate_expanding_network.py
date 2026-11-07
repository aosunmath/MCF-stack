#!/usr/bin/env python3
"""Shoot a symmetric four-ended planar expander; generate original SVG/JSON.

Standard library only. Normalization: k_vec = X_perp/2, Sigma_t=sqrt(t)Sigma.
See documentation/expanding-network-picture.md for sources and limitations.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def rhs(p):
    x, y, theta = p
    return (math.cos(theta), math.sin(theta),
            (-x * math.sin(theta) + y * math.cos(theta)) / 2)


def integrate(a, step=.005, length=12):
    count = round(length / step)
    step = length / count
    p = (a, 0., math.pi / 3)
    result = [p]
    for _ in range(count):
        k1 = rhs(p)
        k2 = rhs(tuple(v + step * k / 2 for v, k in zip(p, k1)))
        k3 = rhs(tuple(v + step * k / 2 for v, k in zip(p, k2)))
        k4 = rhs(tuple(v + step * k for v, k in zip(p, k3)))
        p = tuple(v + step * (b + 2*c + 2*d + e) / 6
                  for v, b, c, d, e in zip(p, k1, k2, k3, k4))
        result.append(p)
    return result


def shoot(step=.005, length=12):
    lo, hi = 0., 1.
    target = math.pi / 4
    assert integrate(lo, step, length)[-1][2] > target
    assert integrate(hi, step, length)[-1][2] < target
    for _ in range(43):
        a = (lo + hi) / 2
        if integrate(a, step, length)[-1][2] > target:
            lo = a
        else:
            hi = a
    a = (lo + hi) / 2
    return a, integrate(a, step, length)


def svg_drawing(data):
    svg = ET.Element(f'{{{NS}}}svg', {
        'width':'1000', 'height':'570', 'viewBox':'0 0 1000 570',
        'role':'img', 'aria-labelledby':'title description',
        'font-family':'system-ui, -apple-system, Segoe UI, sans-serif'})
    def el(tag, parent=svg, **attrs):
        return ET.SubElement(parent, f'{{{NS}}}{tag}',
                             {k.replace('_','-'):str(v) for k,v in attrs.items()})
    def text(x, y, content, size=16, fill='#526b77', **attrs):
        el('text', x=x, y=y, font_size=size, fill=fill, **attrs).text=content
    def path(points, parent=svg, **attrs):
        return el('path', parent, d='M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in points),
                  fill='none', stroke_linecap='round', stroke_linejoin='round', **attrs)
    el('title', id='title').text='Same four rays, two expanding trees'
    el('desc', id='description').text=(
        'Numerical solutions of the planar expander ODE at t=1. A blue tree has a '
        'horizontal central edge; an orange tree has a vertical central edge. '
        'Each has two 120-degree triple junctions and approaches the same dashed '
        'diagonal rays. The trees differ with the four ends held fixed, and are '
        'related by a quarter-turn. All ends continue to infinity.')
    el('rect', width=1000, height=570, fill='#f7fafb')
    text(30, 38, 'Same four rays, two expanding trees', 27, '#183f52', font_weight=650)
    text(30, 67, 'Numerical ODE profiles in ℝ² · t = 1 · equal horizontal and vertical scales', 16)
    defs = el('defs')
    for panel, color in enumerate(['#21667f','#ae6038']):
        left = 24 + panel*488
        el('rect', x=left, y=91, width=464, height=387, rx=12,
           fill='#fff', stroke='#d3e2e8')
        text(left+20, 121, ['Horizontal connection','Vertical connection'][panel], 20, color, font_weight=600)
        clip=el('clipPath',defs,id=f'panel-{panel}')
        el('rect',clip,x=left+14,y=138,width=436,height=305)
        g=el('g',clip_path=f'url(#panel-{panel})')
        cx,cy,scale=left+232,290,80
        def screen(p):
            x,y=p[:2]
            if panel: x,y=-y,x
            return cx+scale*x,cy-scale*y
        for sx in [-1,1]:
            for sy in [-1,1]:
                path([(cx,cy),(cx+sx*400,cy+sy*400)],g,
                     stroke='#a7b5bc',stroke_width=1.8,stroke_dasharray='6 6')
        for indices in data['paths']:
            path([screen(data['vertices'][i]) for i in indices],g,
                 stroke=color,stroke_width=3.3)
        for sign in [-1,1]:
            x,y=screen([sign*data['junction'],0])
            el('circle',g,cx=x,cy=y,r=4.4,fill=color,stroke='white',stroke_width=1.5)
        jx,jy=screen([data['junction'],0])
        angles=[-math.pi/3+i*(2*math.pi/3)/40 for i in range(41)]
        # Arc measures the outward tangents, not finite chords of curved arms.
        angle_points=[]
        for theta in angles:
            dx,dy=18*math.cos(theta),18*math.sin(theta)
            if panel: dx,dy=-dy,dx
            angle_points.append((jx+dx,jy-dy))
        path(angle_points,g,stroke=color,stroke_width=1.2)
        for theta in [-math.pi/3,math.pi/3]:
            dx,dy=29*math.cos(theta),29*math.sin(theta)
            if panel: dx,dy=-dy,dx
            path([(jx,jy),(jx+dx,jy-dy)],g,stroke=color,stroke_width=1,stroke_dasharray='2 3')
        text(jx+(0 if panel else 26),jy+(-33 if panel else 5),'120°',15,color,
             text_anchor='middle' if panel else 'start')
        for x,y,label in [(1.6,1.6,'1'),(-1.6,1.6,'2'),(-1.6,-1.6,'3'),(1.6,-1.6,'4')]:
            # End labels are fixed in the plane, not rotated with the tree.
            text(cx+scale*x+(-14 if x<0 else 8),cy-scale*y+5,label,15,'#526b77')
        text(left+20,462,['Ends 1–4 and 2–3 share junctions','Ends 1–2 and 3–4 share junctions'][panel],16)
    path([(30,507),(64,507)],stroke='#a7b5bc',stroke_width=2,stroke_dasharray='6 6')
    text(76,512,'Prescribed rays / t = 0 limit',16)
    text(520,512,'Two triple junctions · four unbounded ends',16)
    text(30,548,'At positive time: Σₜ = √t Σ₁. The two trees differ with the ends held fixed.',17,'#183f52')
    ET.indent(svg)
    ET.ElementTree(svg).write(OUT/'expanding-network.svg',encoding='utf-8',xml_declaration=True)


def main():
    a, fine = shoot()
    refined_a, refined = shoot(step=.0025)
    longer_a, _ = shoot(length=16)
    # Export at equal arclength intervals .01, retaining tangent angles for audit.
    branch = integrate(a, length=24)[::2]
    vertices, paths = [], []
    for sx, sy in [(1,1),(-1,1),(-1,-1),(1,-1)]:
        start=len(vertices)
        vertices.extend([[round(sx*x,11),round(sy*y,11),0] for x,y,_ in branch])
        paths.append(list(range(start,len(vertices))))
    paths.append([len(vertices),len(vertices)+1])
    vertices.extend([[-a,0,0],[a,0,0]])
    audit={
        'junction_a':a, 'arclength_cutoff':12, 'rk4_step':.005,
        'export_arclength_step':.01, 'display_arclength_cutoff':24,
        'step_halving_junction_difference':abs(a-refined_a),
        'cutoff_extension_junction_difference':abs(a-longer_a),
        'endpoint_tangent_angle_error':abs(fine[-1][2]-math.pi/4),
        'endpoint_distance_to_prescribed_ray':abs(fine[-1][1]-fine[-1][0])/math.sqrt(2),
        'step_halving_max_position_difference':max(math.hypot(p[0]-q[0],p[1]-q[1]) for p,q in zip(fine,refined[::2])),
        'note':'Floating-point consistency checks, not rigorous error bounds or an existence proof.'}
    data={'kind':'expanding-network','status':'numerical-ode',
          'equation':'k_vec = X_perp/2', 'flow':'Sigma_t = sqrt(t) Sigma_1, t > 0',
          'junction':a,'vertices':vertices,'paths':paths,'faces':[],
          'branchAngles':[round(p[2],12) for p in branch],
          'audit':audit}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'expanding-network.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'expanding-network-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    svg_drawing(data)
    print(json.dumps(audit,indent=2))


if __name__=='__main__':
    main()
