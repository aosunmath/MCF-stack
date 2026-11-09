"""Original topology schematics for Chopp's five numerical shrinker candidates.

No shrinker PDE is solved and no paper image or numerical mesh is copied.
See documentation/chopp-review.md. Requires NumPy, SciPy, Pillow,
scikit-image and fast-simplification (the existing geometry environment).
"""
from pathlib import Path
import base64
import io
import json
import math
import numpy as np
from PIL import Image, ImageDraw
from generate_hmw_rays_geometry import make_mesh as closed_mesh
from generate_bns_geometry import make_mesh as saddle_mesh, topology
from generate_iw_geometry import make_mesh as cone_mesh

OUT = Path(__file__).resolve().parents[1] / 'site/assets/solitons'
CASES = {'cube': ('Cubical candidate', 5, 0),
         'octahedron': ('Octahedral candidate', 7, 0),
         'saddle': ('Punctured-torus saddle candidate', 1, 1),
         'two-handle': ('Two-handled cone candidate', 1, 2),
         'four-handle': ('Four-handled cone candidate', 3, 2)}


def make_mesh(case):
    title, genus, ends = CASES[case]
    if case in {'cube', 'octahedron'}:
        data, _ = closed_mesh(case, samples=2200, segments=32, rings=20)
    elif case == 'saddle':
        data, _ = saddle_mesh(1)
        # Rotate xy by pi/4: xy in the drawing field becomes (y²-x²)/2.
        # This gives the reflections stated by Chopp, Section 4.3.
        rot = np.array([[1,-1,0],[1,1,0],[0,0,math.sqrt(2)]])/math.sqrt(2)
        for name in ['vertices','normals']:
            data[name] = (np.array(data[name]) @ rot.T).tolist()
    else:
        data, _ = cone_mesh(genus)
        if case == 'two-handle':
            vertices, normals = np.array(data['vertices']), np.array(data['normals'])
            vertices[:,2] *= 2.5
            normals[:,2] /= 2.5
            normals /= np.linalg.norm(normals,axis=1)[:,None]
            data['vertices'],data['normals'] = vertices.tolist(),normals.tolist()
    # Keep only the fixed topology, never the other paper's genus controls.
    v = np.array(data['vertices']); f = np.array(data['faces'])
    audit = topology(v,f)
    assert audit['components']==1 and audit['genus']==genus and audit['boundary_loops']==ends, audit
    assert audit['boundary_is_manifold'] and max(audit['edge_incidence'])==2
    result = dict(name='chopp-'+case,kind='chopp-topology-schematic',status='schematic',
        vertices=np.round(v,6).tolist(),normals=np.round(data['normals'],6).tolist(),faces=f.tolist(),paths=[],
        genus=genus,ends=ends,cutaway=True,
        view=dict(pitch=.40 if ends else .43,radius=float(np.linalg.norm(v,axis=1).max())),
        viewLabel=f'Schematic · genus {genus} · '+('closed' if not ends else f'{ends} end'+('s' if ends>1 else '')),
        description=f'Original topology schematic for Chopp’s {title.lower()}. Not his numerical data; no shrinker PDE solved.')
    return result,audit


def drawing(case,data):
    title,genus,ends=CASES[case]
    v,f=np.array(data['vertices']),np.array(data['faces'])
    surface=Image.new('RGBA',(2400,1220)); paint=ImageDraw.Draw(surface)
    yaw,pitch=.64,data['view']['pitch'];cy,sy,cp,sp=math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch)
    rot=np.array([[cy,-sy,0],[-sy*sp,-cy*sp,cp],[sy*cp,cy*cp,sp]])
    q=v@rot.T
    scale=min(210/max(abs(q[:,0])),145/max(abs(q[:,1])))
    for cx,cut in [(250,False),(750,True)]:
        xy=np.column_stack([cx+scale*q[:,0],278-scale*q[:,1]])
        for j in np.argsort(q[f,2].mean(axis=1)):
            face=f[j];a,b,c=q[face];n=np.cross(b-a,c-a);n/=np.linalg.norm(n)
            color=np.array([67,139,169] if n[2]>=0 else [215,164,92]);n*=1 if n[2]>=0 else -1
            color=tuple(np.rint(color*(.48+.49*max(0,n@np.array([-.35,.55,.76])))).astype(int))+(255,)
            points=list(xy[face])
            if cut:
                points=[]
                for ia,ib in zip(face,np.roll(face,-1)):
                    ya,yb=v[ia,1],v[ib,1]
                    if ya<=0:points.append(xy[ia])
                    if (ya<=0)!=(yb<=0):points.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
            if len(points)>2:paint.polygon([(round(2.4*x),round(2.4*y)) for x,y in points],fill=color)
    buf=io.BytesIO();surface.save(buf,format='PNG',optimize=True)
    encoded=base64.b64encode(buf.getvalue()).decode()
    topology_text=f'Genus {genus} · '+('closed surface' if not ends else f'{ends} topological end'+('s' if ends>1 else ''))
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 610" role="img" aria-labelledby="title desc">
<title id="title">Chopp: {title}</title><desc id="desc">Original topology schematic, with complete display and cutaway. Not Chopp's computed surface and not a solution of the shrinker equation.</desc>
<rect width="1000" height="610" fill="#f7fafb"/>
<image href="data:image/png;base64,{encoded}" width="1000" height="508.33"/>
<g font-family="Arial, sans-serif" fill="#183f52">
<text x="32" y="42" font-size="27" font-weight="600">Chopp: {title}</text>
<text x="32" y="74" font-size="18">{topology_text} · numerical candidate in the source</text>
<text x="250" y="464" text-anchor="middle" font-size="18">Full display</text>
<text x="750" y="464" text-anchor="middle" font-size="18">Cutaway exposes the interior</text>
<path d="M32 487H968" stroke="#ccdce3"/>
<text x="32" y="520" font-size="19" font-weight="600">SCHEMATIC · no shrinker equation is solved</text>
<text x="32" y="551" font-size="17">Original drawing after Chopp (1994), Section 4. Not the paper's image or numerical mesh.</text>
<text x="32" y="581" font-size="17">Shapes and scale are illustrative. Visible rims and cut edges are display boundaries.</text>
</g></svg>'''
    (OUT/('chopp-'+case+'.svg')).write_text(svg+'\n')


def main():
    audit={}
    for case in CASES:
        data,audit[case]=make_mesh(case)
        (OUT/('chopp-'+case+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
        drawing(case,data)
    (OUT/'chopp-audit.json').write_text(json.dumps(dict(status='topology audit of schematics only',pde_solved=False,models=audit),indent=2)+'\n')
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
