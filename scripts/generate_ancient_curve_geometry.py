"""Exact Stryker–Sun/AAAW curve formulas with scalar inversion for display.

No simulated flow is claimed: vertices sample the formula at the indicated time.
The scalar inverse is computed by bisection and is audited below.
"""
from pathlib import Path
import json,math
from html import escape
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/solitons'

def scale(kind,t):
    if kind=='torus-curve' and t>=0:raise ValueError('Ancient torus curves require t < 0')
    fn=(lambda r:r*r+r**8+2*t) if kind=='torus-curve' else (lambda r:math.log(r)+r*r/2-.5+t)
    lo,hi=0.,max(1.,math.sqrt(max(0.,-2*t if kind=='torus-curve' else 1-2*t)))
    for _ in range(90):
        mid=(lo+hi)/2
        if fn(mid)>0:hi=mid
        else:lo=mid
    return (lo+hi)/2

def points(kind,t,count=600):
    r=scale(kind,t)
    if kind=='torus-curve':return [[r*math.cos(2*math.pi*i/count),r*math.sin(2*math.pi*i/count),r**4*math.cos(4*math.pi*i/count),r**4*math.sin(4*math.pi*i/count)] for i in range(count+1)]
    return [[r*math.cos(s),r*math.sin(s),s] for s in [-2.5*math.pi+5*math.pi*i/count for i in range(count+1)]]

def drawing(name,data):
    pts=[]
    for p in data['vertices']:
        x,y,z=p[:3]
        if len(p)==4:y=y*math.cos(.55)-p[3]*math.sin(.55)
        a=x*math.cos(.64)-y*math.sin(.64);b=x*math.sin(.64)+y*math.cos(.64)
        pts.append((a,z*math.cos(.43)-b*math.sin(.43)))
    xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts);ymin=min(p[1] for p in pts);ymax=max(p[1] for p in pts)
    k=min(500/(xmax-xmin),280/(ymax-ymin));xc=(xmax+xmin)/2;yc=(ymax+ymin)/2
    poly=' '.join(f'{320+k*(x-xc):.3f},{194-k*(y-yc):.3f}' for x,y in pts)
    caption='Exact R4 curve, projected to R3 · t = −1' if name=='ancient-torus-curve' else 'Exact R3 helix · t = 0 · finite viewing window'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 410" role="img"><title>{escape(data["description"])}</title><rect width="640" height="410" fill="#f7fafb"/><polyline points="{poly}" fill="none" stroke="#21667f" stroke-width="3.2"/><text x="320" y="370" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" fill="#355862">{caption}</text><text x="320" y="394" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#5c6d73">Formula sampled after numerical inversion of its exact scalar time relation</text></svg>\n'
    (OUT/(name+'.svg')).write_text(svg)

def main():
    audit={}
    for name,kind,t,tmin,tmax in [('ancient-torus-curve','torus-curve',-1,-6,-.05),('eternal-helix','helix',0,-4,4)]:
        vertices=points(kind,t)
        radius=math.sqrt(-2*tmin) if kind=='torus-curve' else math.hypot(scale(kind,tmin),2.5*math.pi)
        description=('Exact compact ancient curve in R4 with frequencies (1,2), shown by a linear projection; crossings can be projection artifacts.' if kind=='torus-curve' else 'Exact eternal helix in R3, truncated to the parameter range −5π/2 ≤ s ≤ 5π/2; its infinite ends are omitted.')
        data=dict(name=name,vertices=vertices,faces=[],paths=[list(range(len(vertices)))],status='formula',description=description,view={'radius':radius},dynamic={'kind':kind,'min':tmin,'max':tmax,'value':t})
        (OUT/(name+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n');drawing(name,data)
        residuals=[]
        for time in [tmin,t,tmax]:
            r=scale(kind,time)
            residuals.append(abs(r*r+r**8+2*time) if kind=='torus-curve' else abs(math.log(r)+r*r/2-.5+time))
        audit[name]={'formula_status':'exact parametrization; scalar time relation numerically inverted','source':'Stryker–Sun arXiv:1908.02688v2, Sections 2.1–2.2, Appendices A.1–A.2','max_scalar_residual':max(residuals),'times_checked':[tmin,t,tmax],'fixed_view_radius':radius}
    (OUT/'ancient-curve-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
if __name__=='__main__':main()
