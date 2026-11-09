"""Numerical Scherk translator illustration; see documentation/scherk-picture.md.

Needs NumPy, SciPy, contourpy, and Pillow. Use --cache DIRECTORY to reuse
local NPZ grids. The paper and these temporary grids are not published.
"""
from pathlib import Path
import argparse
import base64
import io
import json
import numpy as np
from contourpy import contour_generator
from PIL import Image, ImageDraw
from scherk_solver import solve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
W = np.pi/2
HEIGHT = 1.5


def patch(u, length):
    """Resample level curves; close their tiny unresolved corner to the axis.

Only the displayed patch is reconstructed. This interpolation is not a PDE
solve, and the corner extension is explicitly excluded from error checks.
"""
    m = len(u)//2
    contour = contour_generator(x=np.linspace(0, length/2, m+1),
                                y=np.linspace(0, W/2, m+1), z=u[m:, m:])
    vertices, faces = [], []
    for sx, sy in [(1,1),(-1,1),(-1,-1),(1,-1)]:
        offset = len(vertices)
        for z in np.linspace(-HEIGHT, HEIGHT, 73):
            curves = contour.lines(float(z))
            curve = max(curves, key=len)
            corner = np.array([length/2, W/2])
            if np.linalg.norm(curve[0]-corner) < np.linalg.norm(curve[-1]-corner):
                curve = curve[::-1]
            # The finite graph has discontinuous corner data. Its full limit
            # contains this vertical line, but the small fill is illustrative.
            curve = np.vstack([curve, corner])
            arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))]
            t = np.linspace(0, arc[-1], 41)
            xy = np.column_stack([np.interp(t, arc, curve[:, j]) for j in [0,1]])
            vertices.extend([[sx*x, sy*y, z] for x,y in xy])
        for j in range(72):
            for i in range(40):
                a=offset+j*41+i; b=a+1; c=a+41; d=c+1
                tri=[[a,b,d],[a,d,c]]
                if sx*sy < 0: tri=[f[::-1] for f in tri]
                faces.extend(tri)
    # Weld reflection seams and the four vertical axes.
    merged, remap, lookup = [], [], {}
    for v in vertices:
        key=tuple(np.round(v,7))
        if key not in lookup: lookup[key]=len(merged); merged.append(list(key))
        remap.append(lookup[key])
    faces=[[remap[i] for i in f] for f in faces]
    faces=[f for f in faces if len(set(f))==3]
    vertices, faces = np.asarray(merged), np.asarray(faces)
    normals = np.cross(vertices[faces[:,1]]-vertices[faces[:,0]], vertices[faces[:,2]]-vertices[faces[:,0]])
    flip = normals[:,2] < 0
    faces[flip] = faces[flip,::-1]
    return vertices, faces


def stencil_residual(u, length):
    dx=length/(len(u)-1);dy=W/(len(u)-1);c=u[1:-1,1:-1]
    p=(u[1:-1,2:]-u[1:-1,:-2])/(2*dx)
    q=(u[2:,1:-1]-u[:-2,1:-1])/(2*dy)
    r=(u[1:-1,2:]+u[1:-1,:-2]-2*c)/dx**2
    t=(u[2:,1:-1]+u[:-2,1:-1]-2*c)/dy**2
    s=(u[2:,2:]-u[2:,:-2]-u[:-2,2:]+u[:-2,:-2])/(4*dx*dy)
    return float(np.max(np.abs(((1+q*q)*r-2*p*q*s+(1+p*p)*t)/(1+p*p+q*q)-1)))


def core_audit(u, length):
    dx=length/(len(u)-1);dy=W/(len(u)-1)
    c=u[2:-2,2:-2]
    p=(-u[2:-2,4:]+8*u[2:-2,3:-1]-8*u[2:-2,1:-3]+u[2:-2,:-4])/(12*dx)
    q=(-u[4:,2:-2]+8*u[3:-1,2:-2]-8*u[1:-3,2:-2]+u[:-4,2:-2])/(12*dy)
    r=(-u[2:-2,4:]+16*u[2:-2,3:-1]-30*c+16*u[2:-2,1:-3]-u[2:-2,:-4])/(12*dx*dx)
    t=(-u[4:,2:-2]+16*u[3:-1,2:-2]-30*c+16*u[1:-3,2:-2]-u[:-4,2:-2])/(12*dy*dy)
    s=np.zeros_like(c)
    for i,ci in [(-2,1),(-1,-8),(1,8),(2,-1)]:
        for j,cj in [(-2,1),(-1,-8),(1,8),(2,-1)]:
            s+=ci*cj*u[2+i:len(u)-2+i,2+j:len(u)-2+j]/(144*dx*dy)
    a=np.linspace(-1,1,len(u))[2:-2];X,Y=np.meshgrid(a,a)
    mask=(abs(X)<=.8)&(abs(Y)<=.8)&(abs(c)<=HEIGHT)
    D=1+p*p+q*q
    residual=((1+q*q)*r-2*p*q*s+(1+p*p)*t)/D-1
    return dict(core_fourth_order_operator_residual_max=float(abs(residual[mask]).max()),
                core_gauss_curvature_max=float(((r*t-s*s)/D**2)[mask].max()),
                core_definition='|2x/L| <= 0.8, |2y/w| <= 0.8, |u| <= 1.5; original grid, not resampled corner fills')


def render(data, tiles, size, yaw, pitch, extent):
    im=Image.new('RGB',size,(247,250,251));d=ImageDraw.Draw(im)
    v=np.array(data['vertices']);f=np.array(data['faces'])
    points=[];colors=[]
    for i,j in tiles:
        p=v+[i*data['length'],j*W,0]
        points.append(p)
        colors.extend([([199,130,67] if (i,j)==(0,0) else [61,137,157])]*len(f))
    vv=np.vstack(points);ff=np.vstack([f+k*len(v) for k in range(len(tiles))])
    x,y,z=vv.T;horizontal=x*np.cos(yaw)-y*np.sin(yaw);depth=x*np.sin(yaw)+y*np.cos(yaw)
    q=np.column_stack([horizontal,z*np.cos(pitch)-depth*np.sin(pitch),z*np.sin(pitch)+depth*np.cos(pitch)])
    scale=min(size[0]*.43/extent,size[1]*.40/(2.1 if len(tiles)==1 else 3.8))
    screen=q[:,:2]*[scale,-scale]+[size[0]/2,size[1]/2]
    order=np.argsort(q[ff,2].mean(axis=1))
    for idx in order:
        face=ff[idx];a,b,c=q[face];n=np.cross(b-a,c-a);n/=max(np.linalg.norm(n),1e-12)
        light=.48+.5*abs(np.dot(n,[-.3,.5,.8124]))
        rgb=tuple(np.clip(np.array(colors[idx])*light+8,0,255).astype(int))
        d.polygon([tuple(p) for p in screen[face]],fill=rgb)
    return im


def static_plate(data):
    tiles=[(i,j) for i in range(-2,3) for j in range(-2,3) if (i-j)%2==0]
    panels=[render(data,tiles,(1540,1000),.88,.48,7.8),render(data,[(0,0)],(620,580),.65,.42,1.7)]
    def encoded(im):
        b=io.BytesIO();im.save(b,format='PNG');return base64.b64encode(b.getvalue()).decode()
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="730" viewBox="0 0 1100 730" role="img" aria-labelledby="title desc" font-family="system-ui, sans-serif">
<title id="title">Doubly periodic Scherk translator: numerical construction</title>
<desc id="desc">A finite-boundary numerical translator patch and its half-turn extensions, reflected to the upward convention. The orange central patch repeats on the checkerboard lattice. Small corner fills and the displayed finite ends are approximate.</desc>
<rect width="1100" height="730" fill="#f7fafb"/>
<g fill="#183f52"><text x="32" y="40" font-size="27" font-weight="650">Doubly periodic Scherk translator</text>
<text x="32" y="70" font-size="17">α = π/2 · w = π/2 · upward translation · finite-boundary numerical approximation</text>
<image x="10" y="100" width="770" height="500" href="data:image/png;base64,{encoded(panels[0])}"/>
<image x="770" y="120" width="310" height="290" href="data:image/png;base64,{encoded(panels[1])}"/>
<text x="800" y="120" font-size="19" font-weight="600">One fundamental patch</text>
<text x="800" y="434" font-size="16">L ≈ {data['length']:.4f} &gt; w</text>
<text x="800" y="462" font-size="16">Horizontal edges: +∞</text>
<text x="800" y="490" font-size="16">Vertical edges: −∞</text>
<text x="800" y="529" font-size="15">Half-turn about each</text><text x="800" y="550" font-size="15">vertical corner line.</text>
<circle cx="44" cy="620" r="6" fill="#c78243"/><text x="60" y="626" font-size="18">Central patch</text>
<circle cx="254" cy="620" r="6" fill="#3d899d"/><text x="270" y="626" font-size="18">Repeated half-turn copies</text>
<text x="32" y="665" font-size="16">Numerical graph: edge heights ±2.5; picture cropped to |z| ≤ 1.5. Small corner fills are illustrative.</text>
<text x="32" y="696" font-size="16">Hoffman–Martín–White, Theorem 3.1 and Figures 3, 8–10. No certified error bound.</text></g></svg>'''
    (OUT/'scherk-translators.svg').write_text(svg)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cache',type=Path)
    args=parser.parse_args();grids={}
    if args.cache:
        for key in ['65','129','257','257h2']:
            p=args.cache/f'scherk{key}.npz'
            if p.exists():
                d=np.load(p);grids[key]=(d['u'],float(d['L']))
    if '257' not in grids:
        result=None
        for h in np.arange(1,2.51,.1): result=solve(65,float(h),initial=result)
        grids['65']=result
        for n in [129,257]: result=solve(n,2.5,initial=result);grids[str(n)]=result
    if '257h2' not in grids:
        result=grids['257']
        for h in [2.4,2.3,2.2,2.1,2.0]: result=solve(257,h,initial=result)
        grids['257h2']=result
    for key,(u,length) in grids.items():
        if stencil_residual(u,length)>1e-7:
            raise ValueError(f'Unconverged cached grid: {key}')
    u,length=grids['257'];v,f=patch(u,length)
    audit={k:dict(grid=len(g[0]),boundary_height=float(g[0][0,len(g[0])//2]),length=g[1],stencil_residual_max=stencil_residual(*g),**core_audit(*g)) for k,g in grids.items()}
    for key,(coarse,ell) in grids.items():
        if key=='257':continue
        if len(coarse)==len(u):other=u
        else:other=u[::(len(u)-1)//(len(coarse)-1),::(len(u)-1)//(len(coarse)-1)]
        a=np.linspace(-1,1,len(coarse));X,Y=np.meshgrid(a,a)
        mask=(abs(X)<=.8)&(abs(Y)<=.8)&(abs(other)<=HEIGHT)
        audit[key]['core_height_difference_at_normalized_coordinates']=float(abs(coarse-other)[mask].max())
    data=dict(name='scherk-translators',kind='scherk-numerical',status='numerical-pde-with-corner-fill',
        alpha=np.pi/2,width=W,length=length,boundaryHeight=2.5,displayHeight=HEIGHT,
        vertices=v.tolist(),faces=f.tolist(),paths=[],view=dict(yaw=.88,pitch=.48),
        description='Finite-boundary PDE approximation with interpolated corner fills. No certified error bound.',audit=audit)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'scherk-translators.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'scherk-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    static_plate(data)
    print(json.dumps(dict(vertices=len(v),faces=len(f),audit=audit),indent=2))

if __name__=='__main__':main()
