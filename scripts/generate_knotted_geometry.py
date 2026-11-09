"""Trefoil with three annular ends: topology schematic, not a solved expander.

Mramor--Wang, arXiv:2611.02829v1, Theorem 1.1, Corollary 3.2 and Figure 2.
Regeneration: NumPy, SciPy, scikit-image, fast-simplification, Pillow.
See documentation/knotted-expander-picture.md for the drawing choices.
"""
from collections import Counter, defaultdict
from pathlib import Path
import base64
import io
import json
import numpy as np
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
import fast_simplification
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
CORE = np.array([77, 142, 169])
END_COLORS = np.array([[204, 147, 69], [185, 113, 92], [94, 160, 142]])
AXES = np.array([[0., 1., 0.], [np.sqrt(3)/2, -.5, 0.], [-np.sqrt(3)/2, -.5, 0.]])


def trefoil(t):
    return np.column_stack([np.sin(t)+2*np.sin(2*t), -np.cos(t)+2*np.cos(2*t), .8*np.sin(3*t)])


def clip_plane(vertices, faces, normal, limit):
    points = vertices.tolist(); result = []; cuts = {}
    values = vertices @ normal - limit
    def crossing(a, b):
        key = tuple(sorted((a, b)))
        if key not in cuts:
            cuts[key] = len(points)
            points.append((vertices[a]+(vertices[b]-vertices[a])*values[a]/(values[a]-values[b])).tolist())
        return cuts[key]
    for face in faces.tolist():
        polygon = []
        for a, b in zip(face, face[1:]+face[:1]):
            if values[a] <= 0: polygon.append(a)
            if (values[a] <= 0) != (values[b] <= 0): polygon.append(crossing(a, b))
        for i in range(1, len(polygon)-1): result.append([polygon[0], polygon[i], polygon[i+1]])
    used = sorted({i for face in result for i in face}); lookup = {old: i for i, old in enumerate(used)}
    return np.array(points)[used], np.array([[lookup[i] for i in f] for f in result])


def audit_mesh(vertices, faces):
    edges = Counter(tuple(sorted((int(f[i]), int(f[(i+1)%3])))) for f in faces for i in range(3))
    directed = Counter((int(f[i]), int(f[(i+1)%3])) for f in faces for i in range(3))
    graph = defaultdict(set); boundary = defaultdict(set)
    for (a, b), count in edges.items():
        assert count in [1, 2]
        graph[a].add(b); graph[b].add(a)
        if count == 1: boundary[a].add(b); boundary[b].add(a)
        else: assert directed[a, b] == directed[b, a]
    def components(g):
        remaining = set(g); groups = []
        while remaining:
            group = {remaining.pop()}; pending = list(group)
            while pending:
                for j in g[pending.pop()] & remaining:
                    remaining.remove(j); group.add(j); pending.append(j)
            groups.append(sorted(group))
        return groups
    groups = components(graph); rims = components(boundary)
    assert all(len(v) == 2 for v in boundary.values())
    assert len(groups) == 1 and len(groups[0]) == len(vertices)
    a, b, c = vertices[faces].transpose(1, 0, 2)
    area = np.linalg.norm(np.cross(b-a, c-a), axis=1)/2
    assert area.min() > 1e-10
    chi = len(vertices)-len(edges)+len(faces)
    return dict(vertices=len(vertices), faces=len(faces), components=1,
        boundary_loops=len(rims), euler_characteristic=chi,
        genus=(2-len(rims)-chi)//2, orientable=True,
        minimum_triangle_area=float(area.min()))


def colors_for(v):
    axial = v @ AXES.T
    end = np.argmax(axial, axis=1)
    blend = np.clip((np.max(axial, axis=1)-2.95)/.65, 0, 1)
    blend = blend*blend*(3-2*blend)
    return np.rint(CORE*(1-blend[:, None])+END_COLORS[end]*blend[:, None]).astype(int).tolist()


def make_mesh():
    knot = trefoil(np.linspace(0, 2*np.pi, 1800, endpoint=False))
    tree = cKDTree(knot)
    axis = np.linspace(-5.95, 5.95, 217); height = np.linspace(-1.55, 1.55, 65)
    field = np.empty((len(axis), len(axis), len(height)), dtype=np.float32)
    Y, Z = np.meshgrid(axis, height, indexing='ij')
    for i, x in enumerate(axis):
        p = np.column_stack([np.full(Y.size, x), Y.ravel(), Z.ravel()])
        _, nearest = tree.query(p)
        distance = np.full(len(p), np.inf)
        for shift in [-1, 0]:
            a = knot[(nearest+shift)%len(knot)]; b = knot[(nearest+shift+1)%len(knot)]
            delta = b-a; t = np.clip(np.sum((p-a)*delta, axis=1)/np.sum(delta*delta, axis=1), 0, 1)
            distance = np.minimum(distance, np.linalg.norm(p-a-t[:, None]*delta, axis=1))
        value = distance-.27
        for n in AXES:
            axial = p @ n
            radial = np.linalg.norm(p-axial[:, None]*n, axis=1)
            branch = np.maximum(radial-(.26+.13*(axial-3)), 3-axial)
            # Polynomial smooth union, purely a drawing operation.
            h = np.maximum(.18-np.abs(value-branch), 0)/.18
            value = np.minimum(value, branch)-.18*h*h/4
        field[i] = value.reshape(Y.shape)
    v, f, _, _ = marching_cubes(field, 0, spacing=(axis[1]-axis[0], axis[1]-axis[0], height[1]-height[0]), allow_degenerate=False)
    v += [axis[0], axis[0], height[0]]
    v, f = fast_simplification.simplify(v, f, target_count=23000, agg=4)
    for n in AXES: v, f = clip_plane(v, f, n, 5.2)
    v = np.round(v, 7)
    audit = audit_mesh(v, f)
    assert audit['genus'] == 1 and audit['boundary_loops'] == 3, audit
    assert len(v) < 65536
    data = dict(name='knotted-expanders', kind='knotted-expander-schematic', status='schematic',
        vertices=v.tolist(), faces=f.tolist(), paths=[], vertexColors=colors_for(v),
        spine=np.round(knot[::3], 7).tolist(), endAxes=AXES.tolist(), endColors=END_COLORS.tolist(),
        genus=1, ends=3, view=dict(yaw=.08, pitch=-1.14, radius=5.7),
        construction=dict(tube_radius=.27, end_base=3, end_radius=.26, end_slope=.13,
                          smooth_union=.18, truncation=5.2),
        description='Trefoil tube with three attached flaring annular ends. Topology schematic, not a solved expander or a certified approximation.')
    return data, audit


def closed_core():
    t = np.linspace(0, 2*np.pi, 420, endpoint=False); p = trefoil(t)
    tangent = trefoil(t+1e-5)-trefoil(t-1e-5); tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    n = np.cross(tangent, [0, 0, 1]); n /= np.linalg.norm(n, axis=1)[:, None]
    b = np.cross(tangent, n); phi = np.linspace(0, 2*np.pi, 24, endpoint=False)
    v = (p[:, None, :]+.27*(np.cos(phi)[None, :, None]*n[:, None, :]+np.sin(phi)[None, :, None]*b[:, None, :])).reshape(-1, 3)
    f = []
    for i in range(420):
        for j in range(24):
            a=i*24+j; c=((i+1)%420)*24+(j+1)%24
            f.extend([[a, ((i+1)%420)*24+j, c], [a, c, i*24+(j+1)%24]])
    f = np.array(f); audit = audit_mesh(v, f)
    assert audit['genus'] == 1 and audit['boundary_loops'] == 0
    return dict(vertices=np.round(v, 7).tolist(), faces=f.tolist(), vertexColors=[CORE.tolist()]*len(v))


def render(painter, data, center, scale, limit=5.2, pitch=-1.14):
    v = np.array(data['vertices']); f = np.array(data['faces']); colors = np.array(data['vertexColors'])
    if limit < 5.2:
        for n in AXES: v, f = clip_plane(v, f, n, limit)
        colors = np.array(colors_for(v))
    x, y, z = v.T; yaw=.08
    a=x*np.cos(yaw)-y*np.sin(yaw); b=x*np.sin(yaw)+y*np.cos(yaw)
    q=np.column_stack([a,z*np.cos(pitch)-b*np.sin(pitch),z*np.sin(pitch)+b*np.cos(pitch)])
    xy=np.column_stack([center[0]+scale*q[:,0],center[1]-scale*q[:,1]])
    for j in np.argsort(q[f, 2].mean(axis=1)):
        face=f[j]; a,b,c=q[face]; n=np.cross(b-a,c-a); n/=np.linalg.norm(n)
        if n[2]<0:n=-n
        light=.48+.5*max(0,n@np.array([-.35,.55,.76]))
        rgb=np.rint(colors[face].mean(axis=0)*light).astype(int)
        painter.polygon([tuple(p*3) for p in xy[face]], fill=tuple(rgb)+(255,))


def drawing(data, core, construction=False):
    width,height = (1100,650) if construction else (900,620)
    surface=Image.new('RGBA',(width*3,height*3)); painter=ImageDraw.Draw(surface)
    if construction:
        render(painter,core,(183,277),46)
        render(painter,data,(550,277),46,3.35)
        render(painter,data,(917,277),29.5)
    else: render(painter,data,(450,322),41)
    image=io.BytesIO();surface.resize((width*2,height*2),Image.Resampling.LANCZOS).save(image,format='PNG')
    title='From a trefoil tube to a three-ended surface' if construction else 'Knotted self-expanders: a trefoil with three ends'
    text=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{title}</title>',
        '<desc id="desc">Original topology schematic based on Mramor and Wang, Theorem 1.1 and Corollary 3.2. A trefoil tube is punctured three times and continued into three open annular ends. Not a computed self-expander.</desc>',
        f'<rect width="{width}" height="{height}" fill="#f7fafb"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        f'<text x="30" y="43" font-size="27" font-weight="600">{title}</text>',
        '<text x="30" y="73" font-size="17" fill="#58727e">Mramor–Wang · genus 1, three ends · topology schematic</text>',
        f'<image width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(image.getvalue()).decode()}"/>']
    if construction:
        for x,label,detail in [(183,'1. Thicken the knot','Boundary of a knotted solid torus'),(550,'2. Remove three disks','Three boundary circles; genus still 1'),(917,'3. Attach annular ends','Three open ends; genus still 1')]:
            text.extend([f'<text x="{x}" y="445" font-size="19" font-weight="600" text-anchor="middle">{label}</text>',f'<text x="{x}" y="473" font-size="15" text-anchor="middle">{detail}</text>'])
        text.extend(['<path d="M340 280h45m-10-7 10 7-10 7M708 280h45m-10-7 10 7-10 7" fill="none" stroke="#8b9fa8" stroke-width="2"/>',
            '<text x="30" y="535" font-size="17">The proof protects the overpass bridges with expanding annular barriers (Figure 2).</text>',
            '<text x="30" y="565" font-size="17">This plate illustrates the topology in Theorem 1.1; it does not reproduce the Plateau construction.</text>',
            '<text x="30" y="603" font-size="16" fill="#58727e">The shown flares are chosen for the drawing. No self-expander equation has been solved.</text>'])
    else:
        for x,y,label,color in [(433,113,'End 1','#b67b2b'),(670,460,'End 2','#a15d48'),(240,453,'End 3','#3e8272')]:
            text.append(f'<text x="{x}" y="{y}" font-size="17" font-weight="600" text-anchor="middle" fill="{color}">{label}</text>')
        text.extend(['<text x="30" y="501" font-size="19" font-weight="600">A two-dimensional surface, with visible over / under crossings</text>',
            '<text x="30" y="533" font-size="17">The colored openings are display cuts through three noncompact annular ends.</text>',
            '<text x="30" y="565" font-size="17">The actual expander has asymptotically conical ends; their shape is not computed here.</text>',
            '<text x="30" y="597" font-size="16" fill="#58727e">Rotate and zoom in the reader. The schematic is not a numerical solution of the expander PDE.</text>'])
    text.append('</g></svg>')
    return '\n'.join(text)+'\n'


def main():
    data,audit=make_mesh(); core=closed_core(); data['core']=core
    (OUT/'knotted-expanders.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'knotted-expanders.svg').write_text(drawing(data,core))
    (OUT/'knotted-expander-construction.svg').write_text(drawing(data,core,True))
    (OUT/'knotted-expander-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit))


if __name__=='__main__':main()
