#!/usr/bin/env python3
"""Original exact-coordinate projections, numerical quadratures, and labeled diagrams.

No source figures are copied. Run with Python's standard library. Quadratures
sample exact integral parametrizations; they are not certified error bounds.
"""
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

OUT = Path(__file__).resolve().parents[1] / 'site/assets/solitons'
BLUE, INK, MUTED = '#438ba9', '#183f52', '#526b78'


def node(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def text(svg, x, y, value, size=16, **kw):
    node(svg, 'text', x=x, y=y, font_size=size, fill=INK, **kw).text = value


def canvas(title, subtitle):
    svg = ET.Element('svg', {'xmlns': 'http://www.w3.org/2000/svg', 'viewBox': '0 0 960 610', 'role': 'img', 'aria-labelledby': 'title desc'})
    node(svg, 'title', id='title').text = title
    node(svg, 'desc', id='desc').text = subtitle
    node(svg, 'rect', width=960, height=610, fill='#f7fafb')
    group = node(svg, 'g', font_family='Arial, Helvetica, sans-serif')
    text(group, 30, 42, title, 25, font_weight=600)
    text(group, 30, 70, subtitle, 15)
    return svg, group


def save(svg, name):
    ET.ElementTree(svg).write(OUT / (name + '.svg'), encoding='unicode')


def path(svg, points, color=BLUE, width=3, closed=False):
    node(svg, 'path', d='M ' + ' L '.join(f'{x:.3f},{y:.3f}' for x, y in points) + (' Z' if closed else ''), fill='none', stroke=color, stroke_width=width)


def mobius(theta, r):
    return [math.cosh(r)*math.cos(2*theta), math.cosh(r)*math.sin(2*theta),
            math.sqrt(2)*math.sinh(r)*math.cos(theta), -math.sqrt(2)*math.sinh(r)*math.sin(theta)]


def rotating(x, s):
    return [x*math.cos(s), x*math.sin(s), x*x/2, -s]


def quadratures(alpha, count, ymax=2.8, steps=2800):
    """Equal a_j=1; composite Simpson integration from zero, then odd extension."""
    def p(y):
        return math.expm1(count*math.log1p(y*y)+alpha*y*y)/(y*y) if y else count+alpha
    def integrand(y):
        b=1/math.sqrt(p(y))
        return b/(1+y*y), b
    h=ymax/steps
    phases=[0.0]; heights=[0.0]
    for i in range(steps):
        a,b,c=integrand(i*h),integrand((i+.5)*h),integrand((i+1)*h)
        phases.append(phases[-1]+h*(a[0]+4*b[0]+c[0])/6)
        heights.append(heights[-1]+h*(a[1]+4*b[1]+c[1])/6)
    def at(y):
        q=min(steps,abs(y)/h);i=min(steps-1,int(q));f=q-i;sign=-1 if y<0 else 1
        return tuple(sign*(values[i]*(1-f)+values[i+1]*f) for values in (phases,heights))
    return at


def seed_gradient(x,y):
    s=x*x+y*y
    if not s:return [0,0,0,0]
    return [x,-x/10+1e-4*(4*x**3/s-2*x**5/s**2),y,y/2-2e-4*x**4*y/s**2]


def grid(f, nu, nv, ur, vr, periodic=False, twist=False):
    rows=nu if periodic else nu+1
    vertices=[f(ur[0]+(ur[1]-ur[0])*i/nu,vr[0]+(vr[1]-vr[0])*j/nv)
              for i in range(rows) for j in range(nv+1)]
    faces=[]
    for i in range(nu):
        for j in range(nv):
            a=i*(nv+1)+j;b=a+1
            ii=(i+1)%rows
            jj=nv-j if twist and i==nu-1 else j
            kk=nv-j-1 if twist and i==nu-1 else j+1
            c=ii*(nv+1)+jj;d=ii*(nv+1)+kk
            faces.extend([[a,c,d],[a,d,b]])
    return vertices,faces


def render(name,title,subtitle,vertices,faces,status,footer):
    data=dict(name=name,vertices=vertices,faces=faces,paths=[],status=status,
              description=subtitle,viewLabel='Projection from R4 · crossings may be projection artifacts',view={'pitch':.43})
    (OUT/(name+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
    svg,g=canvas(title,subtitle)
    q=[]
    for x,y,z,w in vertices:
        y=y*math.cos(.55)-w*math.sin(.55)
        h=x*math.cos(.64)-y*math.sin(.64);depth=x*math.sin(.64)+y*math.cos(.64)
        q.append((h,z*math.cos(.43)-depth*math.sin(.43),z*math.sin(.43)+depth*math.cos(.43)))
    lo=[min(p[i] for p in q) for i in range(2)];hi=[max(p[i] for p in q) for i in range(2)]
    scale=min(830/(hi[0]-lo[0]),400/(hi[1]-lo[1]))
    xy=[(480+scale*(p[0]-(lo[0]+hi[0])/2),305-scale*(p[1]-(lo[1]+hi[1])/2)) for p in q]
    for face in sorted(faces,key=lambda f:sum(q[i][2] for i in f)):
        a,b,c=[q[i] for i in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(x*x for x in normal));shade=.45+.5*abs(sum(a*b for a,b in zip(normal,[.3,.5,.8]))/(length or 1))
        rgb=tuple(int(b*shade+63*(1-shade)) for b in [67,139,169])
        node(g,'polygon',points=' '.join(f'{xy[i][0]:.2f},{xy[i][1]:.2f}' for i in face),fill='rgb'+str(rgb),stroke='#24566b',stroke_width='.25',stroke_opacity='.2')
    for j,line in enumerate(footer):text(g,30,552+j*25,line,15)
    save(svg,name)


def diagrams():
    svg,g=canvas('Compact periodic Lagrangian shrinkers','Construction diagram · no ODE closing problem is solved in this picture')
    boxes=[(45,130,'ODE orbit','u(s), phases φⱼ(s)'),(505,130,'Phase closing','γⱼ / π are rational'),(45,330,'Moving quadric','x ∈ Sⁿ⁻¹; wⱼ(s) ∈ C'),(505,330,'Compact immersion','Sⁿ⁻¹ × S¹ → Cⁿ')]
    for x,y,a,b in boxes:
        node(g,'rect',x=x,y=y,width=400,height=130,rx=16,fill='#e6f0f4',stroke=BLUE)
        text(g,x+25,y+42,a,23);text(g,x+25,y+86,b,20)
    text(g,460,203,'→',30);text(g,460,403,'→',30)
    text(g,30,548,'The domain is a torus when n = 2. Embeddedness is not inferred.',17)
    text(g,30,576,'Constant-radius cases are excluded from this catalogue entry.',16)
    save(svg,'jlt-compact-shrinkers')

    svg,g=canvas('An immortal flow with a circle of limits','Schematic in parameter space · the ambient metric on S² is not round')
    center=(315,315)
    path(g,[(center[0]+145*math.cos(t),center[1]+145*math.sin(t)) for t in [i*math.tau/240 for i in range(241)]],color='#b7783d',width=6)
    path(g,[(315+(145+90*math.exp(-t/9))*math.cos(t),315+(145+90*math.exp(-t/9))*math.sin(t)) for t in [i*30/1200 for i in range(1201)]],width=2)
    text(g,605,230,'Critical circle Z ⊂ RP²',22)
    text(g,605,273,'Each z labels a distinct',19);text(g,605,301,'simple closed g-geodesic Γ(z).',19)
    text(g,605,356,'Every Γ(z) is a subsequential',19);text(g,605,384,'smooth limit of the same flow.',19)
    text(g,30,558,'The drawn spiral represents the slow parameter, not an evolving curve in S².',17)
    save(svg,'aryan-lee')

    svg,g=canvas('A compact Lagrangian neck collapses at infinite time','Topology schematic · regular slices remain embedded; m ≥ 3')
    for cx,neck in [(235,32),(705,9)]:
        for side in [-1,1]:
            node(g,'ellipse',cx=cx+side*100,cy=300,rx=105,ry=115,fill='#e6f0f4',stroke=BLUE,stroke_width=3)
        node(g,'rect',x=cx-50,y=300-neck,width=100,height=2*neck,fill='#e6f0f4')
        path(g,[(cx-50,300-neck),(cx,300-neck*.55),(cx+50,300-neck)])
        path(g,[(cx-50,300+neck),(cx,300+neck*.55),(cx+50,300+neck)])
    text(g,451,308,'→',35)
    text(g,140,470,'Small positive neck',21);text(g,599,470,'Later positive neck',21)
    text(g,30,550,'Tᵐ # Tᵐ → two special Lagrangian tori meeting at one point.',18)
    text(g,30,580,'Neck scale ε(t) is comparable to t⁻¹⁄⁽ᵐ⁻²⁾; no finite-time pinching.',17)
    save(svg,'su-tsai-wood')

    # Lee--Tsai now has a dedicated numerical generator: generate_lee_tsai_flow.py.



def additional_figures():
    # Exact Lee–Wang time plates now have dedicated generators:
    # node scripts/generate_lee_wang.mjs
    # node scripts/generate_lee_wang_expander.mjs

    # The source-reviewed slice and time sequence have their own generator.
    from generate_su_gluing import main as generate_su_gluing
    generate_su_gluing()

    # The exact surface/time figure has its own shared JS formula and generator.
    import subprocess
    subprocess.run(['node', str(OUT.parents[2] / 'scripts/generate_su_wood.mjs')], check=True)

    # Exact Lawlor profiles and time/scale views share one geometry module.
    subprocess.run(['node', str(Path(__file__).with_name('generate_stolarski_su.mjs'))], check=True)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    v,f=grid(mobius,80,48,(0,math.pi),(-1.25,1.25),True,True)
    render('mobius-shrinker','The Lee–Wang Möbius shrinker','Exact coordinates · a projection of an embedded surface in R⁴',v,f,'exact-projection',
           ['A fundamental domain has (θ + π, −r) identified with (θ, r).','Only |r| ≤ 1.25 is shown. The two visible edges form one topological end.'])
    exp=quadratures(.5,2)
    def neck(theta,y):
        phi=exp(y)[0];r=math.sqrt(1+y*y)
        return [r*math.cos(theta)*math.cos(phi),r*math.cos(theta)*math.sin(phi),r*math.sin(theta)*math.cos(phi),r*math.sin(theta)*math.sin(phi)]
    v,f=grid(neck,80,80,(0,math.tau),(-2.8,2.8),True)
    render('jlt-expanders','A Lagrangian expander neck','Numerical quadrature of an exact integral parametrization · projection from C²',v,f,'numerical-quadrature',
           ['a₁ = a₂ = 1, α = 1/2; |y| ≤ 2.8. The surface has two planar ends.','Use 4D rotation in the reader. Projected crossings do not mean self-intersection.'])
    trans=quadratures(1,1)
    def translator(x,y):
        phi,b=trans(y);r=math.sqrt(1+y*y)
        return [x*r*math.cos(phi),x*r*math.sin(phi),(y*y-x*x)/2,b]
    v,f=grid(translator,60,80,(-2.2,2.2),(-2.8,2.8))
    render('jlt-translators','An almost-calibrated Lagrangian translator','Numerical quadrature of an exact integral parametrization · projection from C²',v,f,'numerical-quadrature',
           ['a₁ = α = 1. The translation direction is the real second complex coordinate.','This is a finite patch of a complete embedded plane in R⁴.'])
    v,f=grid(rotating,50,150,(-2.4,2.4),(-2*math.pi,2*math.pi))
    render('jlt-rotating-translators','An explicit rotating Lagrangian translator','Exact coordinates · projection of X(x,s) = (x eⁱˢ, x²/2 − is) in C²',v,f,'exact-projection',
           ['The last imaginary coordinate separates successive turns; the surface is embedded.','Only |x| ≤ 2.4 and |s| ≤ 2π are shown. The lifted angle is s − π/2.'])
    def lawlor(theta,y):
        a=math.sqrt(1+y*y/2);b=y/math.sqrt(2)
        return [a*math.cos(theta),b*math.cos(theta),a*math.sin(theta),b*math.sin(theta)]
    v,f=grid(lawlor,80,80,(0,math.tau),(-2.8,2.8),True)
    render('lawlor-necks','A stationary Lawlor neck','Exact coordinates · projection of a special Lagrangian annulus in C²',v,f,'exact-projection',
           ['a₁ = a₂ = 1; α = 0. This is a minimal surface, constant under mean curvature flow.','The full surface has two planar ends; the drawing is truncated at |y| = 2.8.'])
    v,f=grid(lambda theta,r:seed_gradient(r*math.cos(theta),r*math.sin(theta)),100,32,(0,math.tau),(.025,2.8),True)
    render('ttw-expanders','Initial cone for a graphical Lagrangian expander','Exact initial gradient cone · this is not the positive-time expander',v,f,'exact-initial-projection',
           ['U₀ = −x₁²/20 + x₂²/4 + 10⁻⁴ x₁⁴/|x|². The small tip is omitted for display.','The theorem constructs the smooth expander by a parabolic PDE, not this mesh.'])
    diagrams()
    additional_figures()
    fine=quadratures(.5,2,steps=5600)
    error=max(abs(exp(y)[0]-fine(y)[0]) for y in [2.8*i/70 for i in range(71)])
    audit={'status':'Illustration diagnostics, not proof certification','expander_quadrature_refinement_max':error,
           'mobius_fundamental_domain':'0 <= theta < pi, with the last mesh seam reversing r',
           'coordinate_order':'Re z1, Im z1, Re z2, Im z2',
           'ttw_picture':'Exact initial cone only; no PDE solution is computed',
           'schematics':['jlt-compact-shrinkers','aryan-lee','su-tsai-wood']}
    (OUT/'lagrangian-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
