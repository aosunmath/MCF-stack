"""Numerical weighted quotient flow and an original circle-fiber diagram.

Lee--Tsai, arXiv:2606.28767v1, (2.2), (3.2), Remark 6.3.
Requires NumPy and SciPy; run separately from the standard website build.
The plotted surface is NOT an isometric embedding in Euclidean three-space.
"""
from pathlib import Path
import json
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
CENTERS = np.linspace(-1, 1, 4)
COLORS = ['#287c91', '#ba7244', '#796b9c']
TIMES = np.linspace(0, 12, 121)


def grid(n):
    """Sinh grading toward every center; retain shared centers exactly once."""
    q = .5 * np.sinh(5 * np.linspace(0, 1, n // 2 + 1)) / np.sinh(5)
    q = np.r_[q, 1 - q[-2::-1]]
    return np.r_[*[a + (b-a)*q[:-1] for a, b in zip(CENTERS[:-1], CENTERS[1:])], 1.]


def potential(x, u):
    with np.errstate(divide='ignore'):
        return np.sum(.5 / np.hypot(np.asarray(x)[..., None]-CENTERS, np.asarray(u)[..., None]), axis=-1)


def derivatives(x, u):
    hl, hr = np.diff(x)[:-1], np.diff(x)[1:]
    first = (hl**2*(u[2:]-u[1:-1]) + hr**2*(u[1:-1]-u[:-2]))/(hl*hr*(hl+hr))
    second = 2*((u[2:]-u[1:-1])/hr - (u[1:-1]-u[:-2])/hl)/(hl+hr)
    return first, second


def solve(n, rtol=2e-9, atol=2e-12):
    x = grid(n)
    def rhs(t, interior):
        u = np.r_[0, interior, 0]
        ux, uxx = derivatives(x, u)
        return uxx / (potential(x[1:-1], interior)*(1+ux*ux))
    m = len(x)-2
    sparsity = diags([np.ones(m-1), np.ones(m), np.ones(m-1)], [-1, 0, 1])
    result = solve_ivp(rhs, [0, 12], .06*(1-x[1:-1]**2), method='BDF',
                       t_eval=TIMES, rtol=rtol, atol=atol, jac_sparsity=sparsity)
    if not result.success:
        raise RuntimeError(result.message)
    return x, np.pad(result.y.T, ((0, 0), (1, 1)))


def comparison(a, b):
    x, u = a
    y, v = b
    errors = np.array([np.max(np.abs(p-np.interp(x, y, q))) for p, q in zip(u, v)])
    return {'max_absolute_height_difference': float(max(errors)),
            'max_relative_to_frame_height': float(max(errors / np.max(u, axis=1)))}


def project(x, r, theta):
    # Consistent oblique view of (x, r cos(theta), r sin(theta)).
    y, z = r*math.cos(theta), r*math.sin(theta)
    return [x*math.cos(.1)-y*math.sin(.1), z*math.cos(.18)-(x*math.sin(.1)+y*math.cos(.1))*math.sin(.18), z*math.sin(.18)+(x*math.sin(.1)+y*math.cos(.1))*math.cos(.18)]


def svg(data):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 910" role="img" aria-labelledby="title desc">',
             '<title id="title">A smooth sphere approaches a three-sphere chain</title>',
             '<desc id="desc">Numerical weighted quotient flow at t=0, 3 and 12, with a separate infinite-time limit. Circle-fiber size diagrams show two necks narrowing. They are not Euclidean embeddings of the four-dimensional geometry.</desc>',
             '<rect width="960" height="910" fill="#f7fafb"/>',
             '<g font-family="system-ui, sans-serif" fill="#203f50">']
    def text(x,y,s,size=16):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}">{s}</text>')
    def path(points,color,width=2,fill='none'):
        d='M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in points)
        parts.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{width}"/>')
    text(28,35,'One sphere, two narrowing necks',25)
    text(28,63,'Numerical quotient flow · circle-fiber size diagram · four-dimensional ambient space',16)
    for k,index in enumerate([0,30,120,None]):
        left=22+(k%2)*469;top=85+(k//2)*360
        parts.append(f'<rect x="{left}" y="{top}" width="447" height="346" rx="10" fill="white" stroke="#d7e2e7"/>')
        text(left+16,top+28,'Limit t → ∞' if index is None else f't = {data["frames"][index]["time"]:g}',20)
        text(left+16,top+52,'Three spheres; two junctions' if index is None else 'One smooth sphere; both necks positive',14)
        u=np.zeros(len(data['x'])) if index is None else np.array(data['frames'][index]['u'])
        x=np.array(data['x'])[::4];u=u[::4];r=1/np.sqrt(potential(x,u));scale=172;cx=left+224;cy=top+148
        faces=[]
        for i in range(len(x)-1):
            band=min(2,int((.5*(x[i]+x[i+1])+1)*1.5))
            for j in range(24):
                vertices=[project(x[a],r[a],2*math.pi*b/24) for a,b in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]]
                faces.append((sum(v[2] for v in vertices),vertices,band,j))
        for _,v,band,j in sorted(faces,key=lambda f:f[0]):
            c=COLORS[band];shade=.68+.29*abs(math.sin((j+.5)*math.pi/12+.4))
            rgb=[int(int(c[i:i+2],16)*shade) for i in [1,3,5]]
            fill='#'+''.join(f'{a:02x}' for a in rgb)
            path([(cx+scale*p[0],cy-scale*p[1]) for p in v]+[(cx+scale*v[0][0],cy-scale*v[0][1])],fill,.25,fill)
        for j in [25,50]:
            points=[project(x[j],r[j],k*math.pi/32) for k in range(65)]
            path([(cx+scale*p[0],cy-scale*p[1]) for p in points],'#e3ac52',1.7)
        # Quotient graphs use the same fixed vertical magnification in every panel.
        base=top+314
        path([(left+34,base),(left+413,base)],'#b6c5cd',1)
        for i,a in enumerate(CENTERS):
            xp=left+224+a*185
            parts.append(f'<circle cx="{xp:.2f}" cy="{base}" r="3.5" fill="#203f50"/>')
        path([(left+224+185*a,base-185*6*b) for a,b in zip(x,u)],'#287c91',2.5)
        text(left+16,top+335,'Quotient y × 6; fixed scales throughout',12)
    text(28,845,'Circle radius = φ⁻¹ᐟ². Colors mark the three intervals between centers.',17)
    text(28,873,'The 3D diagram does not depict the transverse intersection angles in the actual 4D space.',15)
    text(28,898,'Lee–Tsai (2026), equation (3.2), Theorem 6.2 and Remark 6.3.',13)
    parts.append('</g></svg>')
    (OUT/'lee-tsai.svg').write_text('\n'.join(parts)+'\n')


def main():
    coarse,medium,fine=solve(200),solve(400),solve(800)
    tighter=solve(800,rtol=2e-10,atol=2e-13)
    x,u=fine
    # Cosine sampling resolves all four collapsed fibers and the two narrow waists.
    q=(1-np.cos(np.linspace(0,np.pi,101)))/2
    display_x=np.r_[*[a+(b-a)*q[:-1] for a,b in zip(CENTERS[:-1],CENTERS[1:])],1.]
    frames=[]
    for t,row in zip(TIMES,u):
        heights=np.interp(CENTERS[1:-1],x,row)
        frames.append({'time':round(float(t),8),'u':np.interp(display_x,x,row).round(11).tolist(),
                       'height':float(max(row)),
                       'neckRadii':(1/np.sqrt(potential(CENTERS[1:-1],heights))).tolist()})
    audit={'status':'Numerical consistency checks; not certified error bounds or a proof of the theorem hypotheses.',
           'source':'https://arxiv.org/html/2606.28767v1',
           'equation':'u_t = u_xx / (phi(x,u,0) * (1+u_x^2)); u(-1,t)=u(1,t)=0',
           'centers':CENTERS.tolist(),'regular_potential':0,'initial':'u(x,0)=0.06*(1-x*x)',
           'method':'Nonuniform three-point differences, method of lines, SciPy BDF; sinh mesh grading 5.',
           'mesh_points':[len(s[0]) for s in [coarse,medium,fine]],
           'coarse_to_medium':comparison(coarse,medium),'medium_to_fine':comparison(medium,fine),
           'time_tolerance_refinement':comparison(fine,tighter),
           'minimum_interior_height':float(u[:,1:-1].min()),
           'maximum_temporal_height_increase':float(np.diff(u,axis=0).max()),
           'maximum_discrete_second_derivative':float(max(derivatives(x,row)[1].max() for row in u)),
           'maximum_reflection_error':float(max(abs(row-np.interp(-x,x,row)).max() for row in u)),
           'display':'Quotient vertical scale 6; orbit-radius surface uses (x, phi^(-1/2) cos(theta), phi^(-1/2) sin(theta)). Not an isometric embedding or a Euclidean MCF.',
           'limit':'u=0 is rendered separately and never assigned a finite time; adjacent lifted spheres intersect transversely in 4D.',
           'smallness':'The source gives an existential slope threshold. This chosen numerical initial datum is not certified against that threshold.'}
    assert audit['minimum_interior_height']>0
    assert audit['maximum_temporal_height_increase']<1e-10
    assert audit['maximum_discrete_second_derivative']<1e-7
    assert audit['medium_to_fine']['max_absolute_height_difference']<1e-6
    data={'name':'lee-tsai','kind':'lee-tsai-weighted-flow','status':'numerical-pde-with-fiber-diagram',
          'centers':CENTERS.tolist(),'regularPotential':0,'x':display_x.round(12).tolist(),
          'frames':frames,'vertices':[[float(a),float(b),0] for a,b in zip(display_x,frames[0]['u'])],
          'faces':[],'paths':[list(range(len(display_x)))], 'audit':audit}
    (OUT/'lee-tsai.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'lee-tsai-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    svg(data)
    print(json.dumps(audit,indent=2))

if __name__=='__main__':
    main()
