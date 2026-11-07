"""Original topology schematics inspired by HMW Theorem 24; no PDE is solved.

Requires NumPy, SciPy and Pillow to regenerate. The committed SVG supplies
its vector label layout. See documentation/hmw-rays-picture.md.
"""
from pathlib import Path
import base64
import io
import itertools
import json
import math
import re
import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw
from generate_spherical_doubling_geometry import orient_and_audit

OUT = Path(__file__).resolve().parents[1] / 'site/assets/solitons'
CASES = ['tetrahedron','cube','octahedron','dodecahedron','icosahedron',
         'polygon-3','polygon-5','polygon-7','polygon-12']
COLORS = np.array([[72,139,160],[213,169,105],[170,115,74]])


def rays(case):
    """Face normals of the named solid, or vertices of an equatorial polygon."""
    phi = (1+math.sqrt(5))/2
    if case == 'tetrahedron':
        q = [[a,b,c] for a,b,c in itertools.product([-1,1],repeat=3) if a*b*c == 1]
    elif case == 'cube':
        q = np.vstack([np.eye(3),-np.eye(3)])
    elif case == 'octahedron':
        q = list(itertools.product([-1,1],repeat=3))
    elif case == 'dodecahedron':
        q = [np.roll([0,a,b*phi],j) for j in range(3) for a,b in itertools.product([-1,1],repeat=2)]
    elif case == 'icosahedron':
        q = list(itertools.product([-1,1],repeat=3))
        q += [np.roll([0,a*phi,b/phi],j) for j in range(3) for a,b in itertools.product([-1,1],repeat=2)]
    elif case in CASES:
        n = int(case.split('-')[1])
        q = [[math.cos(2*math.pi*j/n),math.sin(2*math.pi*j/n),0] for j in range(n)]
    else:
        raise ValueError(case)
    q = np.array(q,dtype=float)
    return q/np.linalg.norm(q,axis=1)[:,None]


def base_radius(u, case):
    if case == 'cube':
        return 1.64 / np.sum(u**4,axis=-1)**.25
    return np.full(u.shape[:-1],2.)


def make_mesh(case, samples=4200, segments=40, rings=32):
    sites = rays(case)
    separation = np.arccos(np.clip(sites @ sites.T,-1,1))+np.eye(len(sites))*10
    cap = min(.53,.37*separation.min()); waist = .46*cap; gap = min(.34,.80*cap)
    theta = np.linspace(0,2*math.pi,segments,endpoint=False)
    def directions(n, angle):
        e1 = np.cross(np.eye(3)[np.argmin(abs(n))],n); e1 /= np.linalg.norm(e1)
        e2 = np.cross(n,e1)
        return math.cos(angle)*n + math.sin(angle)*(np.cos(theta)[:,None]*e1+np.sin(theta)[:,None]*e2)
    k = np.arange(samples); z = 1-2*(k+.5)/samples; a = k*math.pi*(3-math.sqrt(5))
    u = np.column_stack([np.sqrt(1-z*z)*np.cos(a),np.sqrt(1-z*z)*np.sin(a),z])
    u = u[np.max(u @ sites.T,axis=1)<math.cos(cap+.018)]
    boundaries = []
    for n in sites:
        boundaries.append(np.arange(len(u),len(u)+segments)); u = np.vstack([u,directions(n,cap)])
    faces = ConvexHull(u).simplices
    faces = faces[np.max(u[faces].mean(axis=1) @ sites.T,axis=1)<math.cos(cap)-1e-10]
    count = len(u); r = base_radius(u,case)
    vertices = np.vstack([(r+gap)[:,None]*u,(r-gap)[:,None]*u]).tolist()
    result = np.vstack([faces,faces+count]).tolist()
    groups = [0]*len(faces)+[1]*len(faces); vertex_groups = [0]*count+[1]*count
    for n,boundary in zip(sites,boundaries):
        loops = [boundary]
        for t in np.linspace(0,math.pi,rings+1)[1:-1]:
            direction = directions(n,cap-(cap-waist)*math.sin(t))
            p = (base_radius(direction,case)+gap*math.cos(t))[:,None]*direction
            loops.append(np.arange(len(vertices),len(vertices)+segments))
            vertices.extend(p.tolist()); vertex_groups.extend([2]*segments)
        loops.append(boundary+count)
        for lower,upper in zip(loops,loops[1:]):
            for i in range(segments):
                j = (i+1)%segments
                result.extend([[lower[i],lower[j],upper[j]],[lower[i],upper[j],upper[i]]]); groups.extend([2,2])
    vertices = np.array(vertices)
    faces,normals,audit = orient_and_audit(vertices,np.array(result))
    assert audit['genus']==len(sites)-1 and len(vertices)<65536
    unit = vertices/np.linalg.norm(vertices,axis=1)[:,None]
    clearance = float(np.arccos(np.clip((unit @ sites.T).max(),-1,1)))
    assert clearance>.99*waist
    audit.update(ray_count=len(sites),minimum_vertex_ray_angle=clearance,
                 cap_angle=float(cap),waist_angle=float(waist),half_gap=float(gap))
    data = dict(name='hmw-platonic-polygon',kind='hmw-ray-schematic',status='schematic',
        case=case,genus=len(sites)-1,rayCount=len(sites),cases=CASES,
        vertices=np.round(vertices,7).tolist(),normals=np.round(normals,7).tolist(),faces=faces.tolist(),paths=[],
        faceGroups=groups,vertexGroups=vertex_groups,palette=COLORS.tolist(),rays=np.round(sites,10).tolist(),
        view=dict(yaw=.62,pitch=.43,radius=2.7),
        construction=dict(cap_angle=float(cap),waist_angle=float(waist),half_gap=float(gap),segments=segments,rings=rings),
        description='Compact topology model inspired by Section 4, Theorem 24. '
        'Not a computed shrinker, a mean curvature flow time slice, or a claim about compactness of the tangent shrinker.')
    return data,audit


def drawing(cube, polygon):
    surface = Image.new('RGBA',(3600,2340)); painter = ImageDraw.Draw(surface)
    cy,sy,cp,sp = math.cos(.62),math.sin(.62),math.cos(.43),math.sin(.43)
    rotation = np.array([[cy,-sy,0],[-sy*sp,-cy*sp,cp],[sy*cp,cy*cp,sp]])
    for cx,data,cut in [(220,cube,False),(620,cube,True),(1000,polygon,False)]:
        v,f = np.array(data['vertices']),np.array(data['faces']); p = v @ rotation.T
        xy = np.column_stack([cx+76*p[:,0],300-76*p[:,1]])
        for j in np.argsort(p[f,2].mean(axis=1)):
            face = f[j]; a,b,c = p[face]; n = np.cross(b-a,c-a); n /= np.linalg.norm(n)
            if n[2]<0: n=-n
            light = .44+.55*max(0,n @ np.array([-.35,.55,.76]))
            color = tuple(np.rint(COLORS[data['faceGroups'][j]]*light).astype(int))+(255,)
            points = list(xy[face])
            if cut:
                points=[]
                for ia,ib in zip(face,np.roll(face,-1)):
                    ya,yb=v[ia,1],v[ib,1]
                    if ya<=0:points.append(xy[ia])
                    if (ya<=0)!=(yb<=0):points.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(points)<3:continue
            painter.polygon([(round(3*x),round(3*y)) for x,y in points],fill=color)
    buffer=io.BytesIO();surface.resize((2400,1560),Image.Resampling.LANCZOS).save(buffer,format='PNG',optimize=True)
    encoded=base64.b64encode(buffer.getvalue()).decode('ascii')
    path=OUT/'hmw-platonic-polygon.svg'
    # Preserve the editable vector headings and captions in the committed plate.
    svg,count=re.subn(r'href="data:image/png;base64,[^"]+"',f'href="data:image/png;base64,{encoded}"',path.read_text())
    assert count==1
    path.write_text(svg)


def main():
    models,audits={},{}
    for case in CASES:
        models[case],audits[case]=make_mesh(case)
        suffix='' if case=='cube' else '-'+case
        (OUT/('hmw-platonic-polygon'+suffix+'.json')).write_text(json.dumps(models[case],separators=(',',':'))+'\n')
    drawing(models['cube'],models['polygon-7'])
    audit=dict(status='schematic',source='https://arxiv.org/abs/2502.20340v3',
        source_locations='Section 4; Theorem 12 and Figure 2, pp. 8–9; Theorem 24, pp. 15–16',pde_solved=False,models=audits)
    (OUT/'hmw-rays-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audits,indent=2))


if __name__=='__main__':main()
