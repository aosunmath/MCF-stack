#!/usr/bin/env python3
"""Original Su construction drawings; exact ingredients, schematic matching.

The three-dimensional Lagrangian lives in C^3. We draw a two-dimensional
z_2=0 slice of an illustrative model in C^3, then project its four remaining
real coordinates. This is NOT a numerical solution of the translator PDE.
Run with Python's standard library; see documentation/su-gluing-picture.md.
"""
import cmath
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

OUT = Path(__file__).resolve().parents[1] / 'site/assets/solitons'
PHI = math.pi / 3
ALPHA = -2 * math.pi / 3
Q = complex(-math.log(math.cos(math.pi / 6)), 2 * math.pi / 3)
EPSILON = .22
BLUE, TEAL, COPPER = (54, 117, 157), (50, 151, 139), (204, 115, 55)


def grim(length, branch=0):
    """Exact unit-speed grim curve, parameterized by intrinsic arc length."""
    l0 = math.asinh(math.tan((-1 if branch == 0 else 1) * math.pi / 6))
    ell = l0 + length
    return complex(math.log(math.cosh(ell)), math.pi / 2 - math.atan(math.sinh(ell)) + branch * PHI)


def neck(s, epsilon=EPSILON):
    """Equal-angle Lawlor profile: Im(w^3)=epsilon^3, 0<arg(w)<pi/3."""
    return epsilon * complex(s, 1) ** (1 / 3)


def smoothstep(x):
    x = max(0., min(1., x))
    return x**3 * (10 - 15*x + 6*x*x)


def point(theta, eta, epsilon=EPSILON, blend=True):
    w = neck(math.sinh(eta), epsilon)
    r = abs(w)
    branch = int(eta < 0)
    mix = smoothstep((r / epsilon - 1.5) / 1.5) if blend else 0.
    z1 = w * math.cos(theta)
    z3 = Q + cmath.exp(1j * ALPHA) * w * math.sin(theta)
    # Coordinate blending is only a drawing device, NOT Su's potential gluing.
    z1 = (1-mix)*z1 + mix*cmath.exp(1j * branch * PHI)*r*math.cos(theta)
    z3 = (1-mix)*z3 + mix*grim(r*math.sin(theta), branch)
    color = [round((1-mix)*a + mix*b) for a,b in zip(COPPER, TEAL if branch else BLUE)]
    return [z1.real, z1.imag, z3.real, z3.imag], color


def geometry():
    nu, nv, radius = 112, 64, 3.5
    limit = math.acosh((radius / EPSILON)**3)
    rows = [point(j*math.tau/nv, -limit + 2*limit*i/nu) for i in range(nu+1) for j in range(nv)]
    vertices, colors = map(list, zip(*rows))
    faces = []
    for i in range(nu):
        for j in range(nv):
            a=i*nv+j; b=i*nv+(j+1)%nv; c=a+nv; d=b+nv
            faces.extend([[a,c,d],[a,d,b]])
    profiles = [[point(sign*math.pi/2, -limit+2*limit*i/400) for i in range(401)] for sign in (-1,1)]
    inputs = [[[0,0,z.real,z.imag] for z in [grim(-3.5+7*i/240, branch) for i in range(241)]] for branch in (0,1)]
    return dict(name='su-glued-translators', kind='su-gluing-slice', status='schematic',
                description='Projected z2=0 slice of an illustrative C3 gluing model; not a solved translator.',
                vertices=vertices, faces=faces, paths=[], vertexColors=colors,
                profiles=[dict(vertices=[p for p,c in row], colors=[c for p,c in row]) for row in profiles],
                inputs=inputs, epsilon=EPSILON, angles=[PHI]*3, shift=0,
                intersection=[Q.real,Q.imag], coordinates=['Re z1','Im z1','Re z3','Im z3'],
                time=dict(min=-1,max=1,initial=0,velocity=[0,0,1,0]),
                view=dict(yaw=.58,pitch=.48),
                source='https://arxiv.org/abs/2011.07882v2',
                sourceLocators=['Main Theorem, p. 3','Sections 3.2–3.4, pp. 8–10','Section 4.1, pp. 11–12','Theorem 6.10, p. 28'])


def node(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k.replace('_','-'):str(v) for k,v in attrs.items()})


def text(g,x,y,value,size=17,**attrs):
    node(g,'text',x=x,y=y,font_size=size,fill='#183f52',**attrs).text=value


def line(g,points,color='#a7bbc5',width=1,**attrs):
    node(g,'path',d='M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in points),fill='none',stroke=color,stroke_width=width,**attrs)


def document(title,description):
    svg=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',viewBox='0 0 1080 650',role='img',attrib={'aria-labelledby':'title desc'})
    node(svg,'title',id='title').text=title
    node(svg,'desc',id='desc').text=description
    node(svg,'rect',width=1080,height=650,fill='#f7fafb')
    g=node(svg,'g',font_family='Arial, Helvetica, sans-serif')
    text(g,32,43,title,27,font_weight=600)
    text(g,32,73,description,15)
    return svg,g


def time_drawing(data):
    svg,g=document('One translator, three times','Selected meridians of a C³ construction model · same axes and scale in every panel')
    for col,t in enumerate((-1,0,1)):
        left=32+350*col
        text(g,left+135,117,f't = {t}',23,text_anchor='middle')
        screen=lambda y,x:(left+28+62*y,495-62*x)
        for x in range(-1,6):
            line(g,[screen(0,x),screen(4.2,x)],'#dce6ea')
            text(g,left+7,screen(0,x)[1]+5,str(x),13)
        for y in range(5):
            line(g,[screen(y,-1),screen(y,5)],'#dce6ea')
            text(g,screen(y,-1)[0],574,str(y),13,text_anchor='middle')
        for curve in data['profiles']:
            for i in range(len(curve['vertices'])-1):
                a,b=curve['vertices'][i:i+2]
                line(g,[screen(a[3],a[2]+t),screen(b[3],b[2]+t)],'rgb(%s)'%','.join(map(str,curve['colors'][i])),3.2,stroke_linecap='round')
        # A fixed spatial reference: dotted p+t e3 track and moving center.
        line(g,[screen(Q.imag,-1.25),screen(Q.imag,1.4)],'#849ca9',1.2,stroke_dasharray='3 5')
        x,y=screen(Q.imag,Q.real+t)
        node(g,'circle',cx=x,cy=y,r=4,fill='#183f52')
        text(g,left+140,603,'Im z₃  →',16,text_anchor='middle')
    text(g,32,147,'Re z₃ ↑',14)
    text(g,32,632,'Lε,t = Lε + t e₃   ·   ε stays fixed   ·   copper: neck and illustrative matching   ·   profiles do not count ends',16)
    ET.ElementTree(svg).write(OUT/'su-glued-times.svg',encoding='unicode')


def profile_drawing(data):
    svg,g=document('Two grim cylinders, one small Lawlor neck','Selected meridians in the z₃-plane · m = 3, equal angles π/3, λ = 0 · construction model')
    # Same spatial scale in the two upper panels. The third panel is a labeled inset.
    for col,title in enumerate(['Exact intersecting inputs','Neck inserted: schematic matching','Neck detail (3×)']):
        left=28+350*col
        text(g,left+150,122,title,18,text_anchor='middle')
        scale=72 if col<2 else 216
        cy=470 if col<2 else 350
        screen=lambda p:(left+150+scale*(p[3]-Q.imag),cy-scale*(p[2]-Q.real))
        for height in range(-1,5):
            line(g,[screen([0,0,height,Q.imag-1.9]),screen([0,0,height,Q.imag+1.9])],'#e1e9ed') if col<2 else None
        if col==0:
            for branch,path in enumerate(data['inputs']):
                line(g,[screen(p) for p in path],'rgb(%s)'%','.join(map(str,[BLUE,TEAL][branch])),3)
            x,y=screen([0,0,Q.real,Q.imag]);node(g,'circle',cx=x,cy=y,r=5,fill='#183f52')
            text(g,left+150,532,'One intersection in C³',16,text_anchor='middle')
        else:
            for curve in data['profiles']:
                for i,(a,b) in enumerate(zip(curve['vertices'],curve['vertices'][1:])):
                    if col==2 and any(abs(p[2]-Q.real)>.72 or abs(p[3]-Q.imag)>.69 for p in (a,b)):continue
                    line(g,[screen(a),screen(b)],'rgb(%s)'%','.join(map(str,curve['colors'][i])),3.2,stroke_linecap='round')
            text(g,left+150,532,'Final PDE correction not drawn' if col==1 else 'ε = 0.22, illustrative',16,text_anchor='middle')
    for i,(color,title) in enumerate([(BLUE,'First grim cylinder'),(COPPER,'Lawlor neck + matching'),(TEAL,'Second grim cylinder')]):
        x=40+i*350;node(g,'circle',cx=x,cy=580,r=6,fill='rgb(%s)'%','.join(map(str,color)));text(g,x+16,586,title,17)
    text(g,32,627,'Horizontal: Im z₃. Vertical: Re z₃. The full translator is three-dimensional in C³; curves do not count ends.',16)
    ET.ElementTree(svg).write(OUT/'su-glued-translators.svg',encoding='unicode')


def main():
    data=geometry()
    (OUT/'su-glued-translators.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    time_drawing(data);profile_drawing(data)


if __name__=='__main__':main()
