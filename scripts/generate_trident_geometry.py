"""Connected trident construction schematic; NOT a numerical translator.

Read documentation/trident-picture.md before interpreting the drawing.
Dependencies: NumPy, scikit-image, fast-simplification, Pillow.
"""
from pathlib import Path
import base64
import io
import json
import numpy as np
from skimage.measure import marching_cubes
import fast_simplification
from PIL import Image, ImageDraw
from generate_kkm_geometry import topology
from generate_nguyen_geometry import render_view

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
SCALES = [.22, .35, .5]
BLUE = np.array([75, 142, 169])
TEAL = np.array([88, 166, 151])
GOLD = np.array([218, 149, 78])


def field(x, y, z, epsilon):
    u = (z + np.log(np.cos(y))) / epsilon
    v = np.arcsinh(np.tan(y)) / epsilon
    return np.tanh(u)*np.tanh(v)-np.sin(x/epsilon)/np.cosh(u)/np.cosh(v)


def make_surface(epsilon):
    # A diffeomorphic image of Scherk: (u,v,w) ->
    # (epsilon*v, atan(sinh(epsilon*w)), epsilon*u+log(cosh(epsilon*w))).
    # Meshing in physical coordinates keeps the three far sheets resolved.
    axes = [np.linspace((-3*np.pi+.13)*epsilon, (3*np.pi+.13)*epsilon, 290),
            np.linspace(-1.565, 1.565, 152), np.linspace(-1.8, 2.8, 194)]
    x,y,z = np.meshgrid(*axes,indexing='ij',sparse=True)
    values = field(x,y,z,epsilon)
    vertices,faces,_,_ = marching_cubes(values.astype(np.float32),0,
        spacing=tuple(a[1]-a[0] for a in axes),allow_degenerate=False)
    vertices += [a[0] for a in axes]
    vertices,faces = fast_simplification.simplify(vertices,faces,target_count=28000,agg=5)
    # Reproject interior vertices after simplification; display boundaries stay put.
    lower=np.array([a[0] for a in axes]);upper=np.array([a[-1] for a in axes])
    edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
    unique,counts=np.unique(edges,axis=0,return_counts=True)
    boundary=np.unique(unique[counts==1])
    fixed=np.zeros(vertices.shape,dtype=bool)
    for i in boundary:
        distances=np.array([abs(vertices[i]-lower),abs(vertices[i]-upper)])
        side,axis=np.unravel_index(np.argmin(distances),distances.shape)
        fixed[i,axis]=True
        vertices[i,axis]=[lower,upper][side][axis]
    for _ in range(5):
        h=1e-5; vals=field(*vertices.T,epsilon)
        grad=np.column_stack([(field(*(vertices+np.eye(3)[i]*h).T,epsilon)-
            field(*(vertices-np.eye(3)[i]*h).T,epsilon))/(2*h) for i in range(3)])
        grad[fixed]=0
        step=vals[:,None]*grad/np.maximum((grad*grad).sum(axis=1)[:,None],1e-20)
        vertices-=step
    # Remove the tiny phase offset from the camera centre, not the geometry.
    x,y,z=vertices.T
    plane=np.exp(-(y/.36)**2)
    color=(1-plane[:,None])*BLUE+plane[:,None]*TEAL
    saddle=np.exp(-((y/(2*epsilon))**2+(z/(2*epsilon))**2))
    color=(1-saddle[:,None])*color+saddle[:,None]*GOLD
    audit=topology(vertices,faces)
    assert audit['components']==1 and audit['edge_incidence']==[1,2],audit
    assert audit['boundary_is_manifold'],audit
    data=dict(name='nguyen-tridents',kind='trident-schematic',status='schematic',
        epsilon=epsilon,period=2*np.pi*epsilon,periods=3,
        vertices=np.round(vertices,9).tolist(),faces=faces.tolist(),paths=[],
        vertexColors=np.rint(color).astype(int).tolist(),
        view=dict(yaw=.78,pitch=-.34,radius=max(3.3,3*np.pi*epsilon),center=[.13*epsilon,0,.5]),
        description='Connected Scherk-to-grim construction schematic, not a solved translator.',
        construction=dict(scherk='sin(v) = sinh(u) sinh(w)',
            map='(x,y,z) = (epsilon*v, atan(sinh(epsilon*w)), epsilon*u + log(cosh(epsilon*w)))',
            bounds=[lower.tolist(),upper.tolist()],half_width=np.pi/2))
    audit['epsilon']=epsilon
    audit['maximum_bounded_field_residual']=float(abs(field(*vertices.T,epsilon)).max())
    return data,audit


def drawing(data):
    image=Image.new('RGBA',(3300,2280));p=ImageDraw.Draw(image)
    display={**data,'vertices':(np.array(data['vertices'])-[0,0,.5]).tolist()}
    render_view(p,display,(365,330),72,.78,-.34)
    render_view(p,display,(895,330),73,1.42,-.08)
    buffer=io.BytesIO();image.resize((2200,1520),Image.Resampling.LANCZOS).save(buffer,format='PNG',optimize=True)
    encoded=base64.b64encode(buffer.getvalue()).decode('ascii')
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 760" role="img" aria-labelledby="title desc">',
      '<title id="title">Nguyen translating tridents: connected saddle construction</title>',
      '<desc id="desc">Three periods of a connected Scherk-based surface with repeated handles. A second view near the periodic direction shows three upper sheets and one lower sheet. This is an illustrative deformation, not a numerical translator.</desc>',
      '<rect width="1100" height="760" fill="#f7fafb"/>',
      f'<image width="1100" height="760" href="data:image/png;base64,{encoded}"/>',
      '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
      '<text x="38" y="48" font-size="28" font-weight="600">Nguyen translating tridents</text>',
      '<text x="38" y="81" font-size="18" fill="#58727e">Periodic Scherk saddles join the grim-reaper wings to the central sheet</text>',
      '<text x="365" y="558" text-anchor="middle" font-size="19" font-weight="600">One connected surface · three periods shown</text>',
      '<text x="895" y="558" text-anchor="middle" font-size="19" font-weight="600">End view</text>',
      '<path d="M1032 465V385m-6 9 6-9 6 9" fill="none" stroke="#183f52" stroke-width="2"/>',
      '<text x="1046" y="430" font-size="17">+z</text>',
      '<circle cx="48" cy="600" r="6" fill="#4b8ea9"/><text x="64" y="606" font-size="17">Grim-reaper wings</text>',
      '<circle cx="310" cy="600" r="6" fill="#da954e"/><text x="326" y="606" font-size="17">Saddle connections</text>',
      '<circle cx="570" cy="600" r="6" fill="#58a697"/><text x="586" y="606" font-size="17">Central sheet</text>',
      '<path d="M38 636H1062" stroke="#cfdee4"/>',
      '<text x="38" y="672" font-size="17">The repeated connections create infinite genus when the strip is continued periodically.</text>',
      '<text x="38" y="710" font-size="17" font-weight="600">CONSTRUCTION SCHEMATIC · not a solved translator · all visible outer edges are display cuts</text>',
      '</g></svg>']
    (OUT/'nguyen-tridents.svg').write_text('\n'.join(parts)+'\n')


def main():
    audits=[]
    for epsilon in SCALES:
        data,audit=make_surface(epsilon);audits.append(audit)
        suffix='' if epsilon==.35 else '-'+str(round(epsilon*100))
        (OUT/f'nguyen-tridents{suffix}.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
        if epsilon==.35:drawing(data)
        print(audit,flush=True)
    (OUT/'trident-audit.json').write_text(json.dumps(dict(status='drawing mesh audit; not translator validation',models=audits),indent=2)+'\n')

if __name__=='__main__':main()
