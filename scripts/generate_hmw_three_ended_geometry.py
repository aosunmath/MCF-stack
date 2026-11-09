"""HMW three-ended topology schematic, NOT a computed shrinker.

Read arXiv:2502.20340v3, Figure 7, Section 8 and Proposition 62.
See documentation/hmw-three-ended-picture.md for provenance and limitations.
Regeneration requires NumPy, SciPy and Pillow. The shared topology audit
checks a mesh only and does not identify HMW with Shao–Zou shrinkers.
"""
from pathlib import Path
import base64
import io
import json
import math
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw
from generate_shao_zou_geometry import audit_mesh, RIM

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
PARAMETERS = [1, 3, 7]
COLORS = np.array([[80,139,166],[119,175,173],[223,181,108],[190,148,112]])


def sheet_height(points, layer, g, amplitude):
    r = np.linalg.norm(points, axis=1)
    if layer == 1:
        theta = np.arctan2(points[:,1], points[:,0])
        # Exact horizontal zero set Q_g in the analytic drawing, smooth at O.
        # This small corrugation is illustrative, not a shrinker eigenfunction.
        return .035*amplitude*r**(g+1)/(1+r*r)**(g/2)*np.sin((g+1)*theta)
    profile = .80+.16*np.sqrt(1+r*r)-.24*np.exp(-((r-1.65)/.5)**2)
    return (layer-1)*amplitude*profile


def make_mesh(g, segments=32, rings=24):
    k, m, radius = 3, g+1, 1.65
    # All neck patches, including staggered patches on intermediate sheets,
    # are disjoint. Widths and heights are enlarged for visibility.
    patch = .72*radius*math.sin(math.pi/(2*m))
    waist = .25*patch
    amplitude = 1.55*patch
    sites = [np.array([[radius*math.cos(2*math.pi*j/m+(1.5-gap)*math.pi/m),
                       radius*math.sin(2*math.pi*j/m+(1.5-gap)*math.pi/m)]
                      for j in range(m)]) for gap in range(k-1)]
    vertices, faces, groups, boundaries = [], [], [], {}
    angles = np.arange(segments)*2*math.pi/segments
    local = np.column_stack([np.cos(angles), np.sin(angles)])
    # Symmetric point samples with explicit circular hole boundaries. Every
    # collar shares its vertex indices with the sheets: no overlay cylinders.
    base = [[0., 0.]]
    for r in np.linspace(.10, RIM, 37):
        count = max(2*m, 2*m*math.ceil(2*math.pi*r/(2*m*.15)))
        theta = np.arange(count)*2*math.pi/count
        base.extend(np.column_stack([r*np.cos(theta), r*np.sin(theta)]))
    base = np.array(base)
    for layer in range(k):
        gaps = [g for g in [layer-1, layer] if 0 <= g < k-1]
        centers = np.concatenate([sites[g] for g in gaps])
        distance = np.linalg.norm(base[:, None, :]-centers[None, :, :], axis=2).min(axis=1)
        points = base[distance > patch+.025]
        offset = len(vertices)
        for gap in gaps:
            for j, site in enumerate(sites[gap]):
                boundaries[layer, gap, j] = np.arange(len(points), len(points)+segments)+offset
                # Rotate local samples with the site to retain discrete symmetry.
                theta = math.atan2(site[1], site[0])
                rotation = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
                points = np.vstack([points, site+patch*(local @ rotation.T)])
        triangles = Delaunay(points).simplices
        centroids = points[triangles].mean(axis=1)
        distances = np.linalg.norm(centroids[:, None, :]-centers[None, :, :], axis=2).min(axis=1)
        triangles = triangles[distances > patch*math.cos(math.pi/segments)]
        z = sheet_height(points, layer, g, amplitude)
        vertices.extend(np.column_stack([points, z]).tolist())
        faces.extend((triangles+offset).tolist()); groups.extend([layer]*len(points))
    umax = math.acosh(patch/waist)
    for gap in range(k-1):
        for j, site in enumerate(sites[gap]):
            theta = math.atan2(site[1], site[0])
            rotation = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
            circle = local @ rotation.T
            loops = [boundaries[gap, gap, j]]
            for u in np.linspace(-umax, umax, rings+1)[1:-1]:
                rho = waist*math.cosh(u)
                p = site+rho*circle
                # Flatten the last collar onto the curved sheet; the central
                # throat retains the cosh profile, with illustrative z scaling.
                t = abs(u)/umax
                w = np.clip((t-.65)/.35, 0, 1)
                w = w*w*w*(10-15*w+6*w*w)
                h = math.copysign((1-w)*t+w, u)
                low = sheet_height(p, gap, g, amplitude)
                high = sheet_height(p, gap+1, g, amplitude)
                z = (low+high)/2+h*(high-low)/2
                loops.append(np.arange(len(vertices), len(vertices)+segments))
                vertices.extend(np.column_stack([p, z]).tolist()); groups.extend([3]*segments)
            loops.append(boundaries[gap+1, gap, j])
            for lower, upper in zip(loops, loops[1:]):
                for a in range(segments):
                    b = (a+1)%segments
                    faces.extend([[lower[a], lower[b], upper[b]], [lower[a], upper[b], upper[a]]])
    vertices = np.array(vertices)
    faces, normals, audit = audit_mesh(vertices, np.array(faces), k, m)
    assert len(vertices) < 65536
    data = dict(name='hmw-three-ended', kind='hmw-three-ended-schematic', status='schematic',
        g=g, genus=2*g, vertices=np.round(vertices, 6).tolist(), faces=faces.tolist(),
        paths=[], vertexGroups=groups, palette=COLORS.tolist(),
        view=dict(yaw=.14, pitch=.22, radius=RIM, gap=1),
        construction=dict(illustrative_radius=radius, patch_radius=patch,
            waist_radius=waist, amplitude=amplitude, sites=[p.tolist() for p in sites],
            segments=segments, rings=rings, display_radius=RIM),
        description='Original topology schematic informed by HMW Figure 7 and Theorem 43. '
        'Three sheets joined by alternating necks. No shrinker PDE or flow is solved. '
        'The displayed small genera are illustrative; existence with three ends is proved only for sufficiently large g.')
    return data, audit


def limiting_plane():
    n=144
    vertices=[[0,0,0]]+[[RIM*math.cos(2*math.pi*j/n),RIM*math.sin(2*math.pi*j/n),0] for j in range(n)]
    return dict(name='hmw-three-plane-limit',kind='hmw-three-ended-limit',status='limiting-configuration',
        vertices=vertices,faces=[[0,j+1,(j+1)%n+1] for j in range(n)],paths=[],
        vertexGroups=[1]*len(vertices),palette=COLORS.tolist(),multiplicity=3,
        view=dict(yaw=.14,pitch=.22,radius=RIM,gap=1),
        description='One horizontal plane with varifold multiplicity three. Not three distinct parallel planes.')


def drawing(data):
    """Original plate; rasterized mesh plus legible vector annotations."""
    vertices=np.array(data['vertices']); faces=np.array(data['faces'])
    palette=COLORS[np.array(data['vertexGroups'])]
    canvas=Image.new('RGBA',(3300,2160)); painter=ImageDraw.Draw(canvas)
    yaw,pitch=.14,.22
    cy,sy,cp,sp=math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch)
    q=vertices@np.array([[cy,-sy,0],[-sy*sp,-cy*sp,cp],[sy*cp,cy*cp,sp]]).T
    for cx,cut in [(275,False),(825,True)]:
        xy=np.column_stack([cx+75*q[:,0],260-75*q[:,1]])
        for i in np.argsort(q[faces,2].mean(axis=1)):
            f=faces[i]; a,b,c=q[f]; n=np.cross(b-a,c-a); n/=np.linalg.norm(n)
            if n[2]<0:n=-n
            light=.52+.47*max(0,n@np.array([-.35,.55,.76]))
            rgb=np.rint(palette[f].mean(axis=0)*light).astype(int)
            polygon=list(xy[f])
            if cut:
                polygon=[]
                for ia,ib in zip(f,np.roll(f,-1)):
                    ya,yb=vertices[ia,1],vertices[ib,1]
                    if ya<=0:polygon.append(xy[ia])
                    if (ya<=0)!=(yb<=0):polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(polygon)<3:continue
            painter.polygon([(round(3*p[0]),round(3*p[1])) for p in polygon],fill=tuple(rgb)+(255,))
    buffer=io.BytesIO(); canvas.resize((2200,1440),Image.Resampling.LANCZOS).save(buffer,format='PNG',optimize=True)
    encoded=base64.b64encode(buffer.getvalue()).decode()
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 720" role="img" aria-labelledby="title desc">',
      '<title id="title">Hoffman–Martín–White three-ended shrinkers: connected topology model</title>',
      '<desc id="desc">Original genus-six schematic: three sheets joined by eight alternating open necks. Full view and cutaway. Three outer rims truncate the ends. Separate plan shows four horizontal lines and alternating neck sites. No shrinker equation has been solved.</desc>',
      '<rect width="1100" height="720" fill="#f7fafb"/>',
      f'<image width="1100" height="720" href="data:image/png;base64,{encoded}"/>',
      '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
      '<text x="34" y="44" font-size="27" font-weight="600">Hoffman–Martín–White: three ends, one connected surface</text>',
      '<text x="34" y="77" font-size="18" fill="#58727e">Topology model with g = 3 · genus 2g = 6 · eight alternating necks</text>',
      '<text x="275" y="400" text-anchor="middle" font-size="19" font-weight="600">Three ends joined through open necks</text>',
      '<text x="825" y="400" text-anchor="middle" font-size="19" font-weight="600">Cutaway reveals the middle sheet</text>',
      '<path d="M34 432H1066" stroke="#cedde3"/>',
      '<text x="34" y="473" font-size="19" font-weight="600">Necks alternate between the two gaps</text>',
      '<text x="34" y="508" font-size="17">Four upper + four lower connections give model genus six.</text>',
      '<text x="34" y="542" font-size="17">The horizontal trace consists of g + 1 equally spaced lines.</text>',
      '<text x="34" y="576" font-size="17">Each exterior sheet continues to an end; all rims are artificial.</text>',
      '<text x="34" y="610" font-size="17">Large-genus limit: one plane with multiplicity three.</text>',
      '<circle cx="880" cy="534" r="76" fill="none" stroke="#99adb5" stroke-dasharray="4 4"/>']
    for j in range(4):
        t=j*math.pi/4;x,y=91*math.cos(t),91*math.sin(t)
        parts.append(f'<path d="M{880-x:.2f} {534-y:.2f}L{880+x:.2f} {534+y:.2f}" stroke="#58727e"/>')
    for gap,color in [(0,'#508ba6'),(1,'#bd8c3f')]:
        for x,y in data['construction']['sites'][gap]:
            parts.append(f'<circle cx="{880+76*x/1.65:.2f}" cy="{534-76*y/1.65:.2f}" r="6" fill="{color}"/>')
    parts+=['<text x="880" y="650" text-anchor="middle" font-size="16">Plan: upper / lower necks</text>',
      '<path d="M34 666H1066" stroke="#cedde3"/>',
      '<text x="34" y="697" font-size="16" font-weight="600">SCHEMATIC · not a computed shrinker · three-ended existence is proved only for sufficiently large g</text>',
      '</g></svg>']
    (OUT/'hmw-three-ended.svg').write_text('\n'.join(parts)+'\n')


def main():
    audits={}
    for g in PARAMETERS:
        data,audit=make_mesh(g);audits[str(g)]=audit
        suffix='' if g==3 else f'-{g}'
        (OUT/f'hmw-three-ended{suffix}.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
        if g==3:drawing(data)
        print(g,audit,flush=True)
    (OUT/'hmw-three-plane-limit.json').write_text(json.dumps(limiting_plane(),separators=(',',':'))+'\n')
    (OUT/'hmw-three-ended-audit.json').write_text(json.dumps(dict(status='schematic',
        source='https://arxiv.org/abs/2502.20340v3',
        source_locations='Figure 7; Theorems 43, 55, 59; Proposition 62',
        models=audits),indent=2)+'\n')


if __name__=='__main__':main()
