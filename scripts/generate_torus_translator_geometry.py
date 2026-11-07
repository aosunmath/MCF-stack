"""Draw Sun–Wang's auxiliary end using the existing numerical Angenent profile.

Standard library only. This does not solve the translator PDE. The quotient
forgets the SO(2) angle in (x1,x2); a horizontal slice restores that angle.
"""
from pathlib import Path
from html import escape
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'


def profile():
    source = OUT / 'angenent-torus.json'
    data = json.loads(source.read_text())
    # generate_soliton_geometry.py uses 49 angular samples per meridian point.
    rings = data['vertices'][::49]
    assert len(rings) == 199 and all(abs(p[1]) < 1e-6 for p in rings)
    assert math.dist(rings[0], rings[-1]) < 1e-6
    return [[p[0], p[2]] for p in rings[:-1:2]], hashlib.sha256(source.read_bytes()).hexdigest()


def mesh(curve, mode='end', height=4, rows=48, sectors=48):
    vertices, faces = [], []
    n = len(curve)
    if mode == 'slice':
        for j in range(sectors):
            theta = 2*math.pi*j/sectors
            for r, q in curve:
                vertices.append([height**.5*r*math.cos(theta),height**.5*r*math.sin(theta),height**.5*q])
        count = sectors
    else:
        for j in range(rows+1):
            h = 1+8*j/rows
            scale = 1 if mode == 'normalized' else h**.5
            for r, q in curve:
                vertices.append([scale*r, scale*q, h])
        count = rows
    for j in range(count):
        jj = (j+1) % sectors if mode == 'slice' else j+1
        for i in range(n):
            a,b,c,d = j*n+i,j*n+(i+1)%n,jj*n+(i+1)%n,jj*n+i
            faces.extend([[a,b,c],[a,c,d]])
    return vertices, faces


def rotate(p, yaw, pitch):
    x,y,z=p
    h=x*math.cos(yaw)-y*math.sin(yaw)
    d=x*math.sin(yaw)+y*math.cos(yaw)
    return [h,z*math.cos(pitch)-d*math.sin(pitch),z*math.sin(pitch)+d*math.cos(pitch)]


def panel(vertices, faces, cx, cy, scale, center, yaw, pitch, color):
    q=[rotate([p[k]-center[k] for k in range(3)],yaw,pitch) for p in vertices]
    xy=[(cx+scale*p[0],cy-scale*p[1]) for p in q]
    elements=[]
    for face in sorted(faces,key=lambda f:sum(q[i][2] for i in f)/3):
        a,b,c=[q[i] for i in face]
        u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(x*x for x in normal)) or 1
        light=.55+.43*abs(sum(x*y for x,y in zip(normal,[-.3,.5,.8]))/length)
        rgb=','.join(str(round(c*light)) for c in color)
        pts=' '.join(f'{xy[i][0]:.2f},{xy[i][1]:.2f}' for i in face)
        elements.append(f'<polygon points="{pts}" fill="rgb({rgb})" stroke="rgb({rgb})" stroke-width=".3"/>')
    return ''.join(elements)


def text(x,y,s,size=14,fill='#183f52'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}">{escape(s)}</text>'


def drawing(curve):
    end,faces=mesh(curve)
    torus,tf=mesh(curve,'slice')
    body=panel(end,faces,187,224,23,[5,0,5],.38,.28,[73,151,177])
    body+=panel(torus,tf,488,217,18,[0,0,0],.64,.79,[196,126,64])
    # The highlighted closed meridian is a guide drawn through the quotient.
    pts=[]
    for r,q in curve+[curve[0]]:
        p=rotate([2*r-5,2*q,-1],.38,.28)
        pts.append(f'{187+23*p[0]:.2f},{224-23*p[1]:.2f}')
    body+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="#ac5927" stroke-width="2.6"/>'
    body+=text(27,31,'A torus-shaped end in four-space',22)
    body+=text(27,55,'Leading model (√z x, z) • numerical Angenent profile • u = 0',14)
    body+=text(27,87,'ROTATIONAL QUOTIENT',12)
    body+=text(385,87,'HORIZONTAL SLICE',12)
    body+=text(381,110,'h = z/z₀ = 4; scale √h = 2',13)
    body+='<path d="M 330 218 L 361 218 M 354 212 L 361 218 L 354 224" fill="none" stroke="#ac5927" stroke-width="2"/>'
    body+=text(29,321,'h = 1',12)+text(29,119,'h = 9',12)
    body+='<path d="M 22 305 L 22 131 M 18 138 L 22 131 L 26 138" fill="none" stroke="#65818f"/>'
    body+=text(83,347,'(r/√z₀, x₃/√z₀, h)',14)
    body+=text(383,331,'Restore the rotation angle',13)
    body+=text(383,350,'to recover a torus in ℝ³.',13)
    body+=text(27,378,'Open rims truncate one end. The compact core is not drawn.',14)
    desc='The numerical Angenent meridian swept with square-root height growth in the rotation quotient, beside its torus slice at relative height four. Copper marks the selected quotient loop through the surface. The auxiliary model sets the unknown translator correction to zero; no compact core or translator PDE solution is shown.'
    (OUT/'sun-wang-torus-end.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc"><title id="title">Angenent-torus translator end: quotient and slice</title><desc id="desc">{escape(desc)}</desc><rect width="640" height="410" fill="#f7fafb"/><g font-family="Arial,Helvetica,sans-serif">{body}</g></svg>\n')


def main():
    curve, sha = profile()
    vertices, faces = mesh(curve)
    audit=json.loads((OUT/'geometry-audit.json').read_text())['angenent-torus']
    data={'name':'sun-wang-torus-end','kind':'torus-translator-end','status':'asymptotic-model',
          'vertices':vertices,'faces':faces,'paths':[],'profile':curve,
          'height_range':[1,9],'height':4,
          'source':{'url':'https://arxiv.org/pdf/2301.08224v2','locators':'Theorem 1.2 (p. 3), Section 5 (pp. 34–35), Appendix A (pp. 39–40)'},
          'profile_source':{'file':'angenent-torus.json','sha256':sha,'audit':audit},
          'normalization':'Hvec(S_A) = -Xperp/2; translator velocity e4',
          'coordinates':'h=z/z0, rho=r/sqrt(z0), eta=x3/sqrt(z0). The quotient omits the rotation angle in (x1,x2).',
          'limitations':'u=0 auxiliary end only. The torus profile is numerical, not a certified approximation. z0 is an unspecified sufficiently large cutoff; h=1 is not the translator tip. Neither the correction, compact core, nor fattening pair is computed.'}
    (OUT/'sun-wang-torus-end.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    drawing(curve)
    print(f'Wrote quotient mesh: {len(vertices)} vertices, {len(faces)} faces; {len(curve)} meridian samples.')


if __name__=='__main__':main()
