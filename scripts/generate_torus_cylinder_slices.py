"""Three R4 slices of the torus-cylinder, using the existing numerical torus.

This is a sampled product visualization, not a new ODE solve. The product
identity is exact; the factor remains a numerical shooting approximation.
Only three two-dimensional slices of the three-dimensional product are drawn.
Requires only Python's standard library.
"""
from pathlib import Path
import json
import math
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
NAME = 'angenent-torus-cylinder'


def main():
    source = json.loads((OUT / 'angenent-torus.json').read_text())
    # The source generator samples 199 profile points and 49 angular points,
    # including both seam copies. Retain both seams while reducing display cost.
    assert len(source['vertices']) == 199 * 49
    profile = range(0, 199, 3)
    angles = range(0, 49, 2)
    base = [source['vertices'][i*49+j] for i in profile for j in angles]
    levels = [-12, 0, 12]
    vertices = [[*p, w] for w in levels for p in base]
    faces, groups = [], []
    m, n = len(profile), len(angles)
    for layer in range(3):
        offset = layer * len(base)
        for i in range(m-1):
            for j in range(n-1):
                a = offset + i*n+j
                faces += [[a,a+n,a+n+1], [a,a+n+1,a+1]]
                groups += [layer, layer]
    description = ('Three selected slices w = -12, 0, 12 of the numerical Angenent '
                   'torus times a line in R4, projected into R3. Not the entire '
                   'three-dimensional hypersurface; crossings are projection artifacts.')
    data = dict(name=NAME, vertices=vertices, faces=faces, paths=[],
                faceGroups=groups, palette=[[67,139,169],[176,115,75],[131,111,162]],
                description=description, status='numerical-product-slices',
                view={'radius':10.2,'pitch':.65},
                slices={'coordinate':3,'values':levels,'intrinsic_dimension':3,
                        'drawn_slice_dimension':2,'factor':'angenent-torus'})
    (OUT/(NAME+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
    points=[]
    for x,y,z,w in vertices:
        y=y*math.cos(.55)-w*math.sin(.55)
        horizontal=x*math.cos(.64)-y*math.sin(.64)
        depth=x*math.sin(.64)+y*math.cos(.64)
        points.append((horizontal,z*math.cos(.65)-depth*math.sin(.65),
                       z*math.sin(.65)+depth*math.cos(.65)))
    scale=min(560/(max(p[0] for p in points)-min(p[0] for p in points)),
              300/(max(p[1] for p in points)-min(p[1] for p in points)))
    xy=[(320+scale*p[0],205-scale*p[1]) for p in points]
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 410" role="img">',
           '<title>'+escape(description)+'</title>',
           '<rect width="640" height="410" fill="#f7fafb"/>']
    for index in sorted(range(len(faces)),key=lambda i:sum(points[j][2] for j in faces[i])):
        face=faces[index];a,b,c=[points[j] for j in face]
        u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        light=.42+.52*abs(sum(a*b for a,b in zip(normal,[.3,.5,.8]))/(math.hypot(*normal) or 1))
        rgb=','.join(str(round(c*light+255*(1-light)*.25)) for c in data['palette'][groups[index]])
        coords=' '.join(f'{xy[j][0]:.2f},{xy[j][1]:.2f}' for j in face)
        parts.append(f'<polygon points="{coords}" fill="rgb({rgb})" stroke="rgb({rgb})" stroke-width=".3"/>')
    parts += ['<g fill="#183f52" font-family="Arial, sans-serif" font-size="16" text-anchor="middle">',
              '<text x="320" y="28">Angenent torus × R: three selected R4 slices</text>',
              '<text x="320" y="388">Numerical factor • projected slices • not three components</text>',
              '</g></svg>']
    (OUT/(NAME+'.svg')).write_text('\n'.join(parts)+'\n')


if __name__ == '__main__':
    main()
