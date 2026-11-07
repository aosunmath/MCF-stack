"""Original qualitative pitchfork drawing, NOT a solved translator.

Read documentation/pitchfork-picture.md for the source and drawing-map audit.
Regenerate with Python, NumPy and Pillow. No paper figures are redistributed.
"""
from pathlib import Path
import base64
import io
import json
import math
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
LIMIT = 6.0
ZMIN, ZMAX = -3.5, 4.5
TEAL, GOLD = np.array([66, 145, 158]), np.array([211, 147, 79])


def drawing_x(y, z):
    return .5*np.sin(y)*np.exp(z) + y*z - np.tan(y/2)


def normal(y, z):
    fy = .5*np.cos(y)*np.exp(z) + z - .5/np.cos(y/2)**2
    fz = .5*np.sin(y)*np.exp(z) + y
    n = np.array([1., -fy, -fz])
    return n/np.linalg.norm(n)


def make_surface():
    # Chebyshev spacing resolves the nearly vertical outer sheets. The exact
    # y=0 row is shared by the two halves, rather than doubled or bridged.
    ys = np.pi*.998*(-np.cos(np.linspace(0, np.pi, 181)))
    ys[90] = 0
    zs = np.linspace(ZMIN, ZMAX, 145)
    grid = [[[float(drawing_x(y,z)),float(y),float(z)] for y in ys] for z in zs]
    vertices, faces, lookup = [], [], {}

    def vertex(p):
        key = tuple(round(float(c), 8) for c in p)
        if key not in lookup:
            lookup[key] = len(vertices)
            vertices.append(key)
        return lookup[key]

    def clipped(poly, side):
        result = []
        for a,b in zip(poly, poly[1:]+poly[:1]):
            ina, inb = side*a[0] <= LIMIT, side*b[0] <= LIMIT
            if ina:
                result.append(a)
            if ina != inb:
                t = (side*LIMIT-a[0])/(b[0]-a[0])
                result.append([a[k]+t*(b[k]-a[k]) for k in range(3)])
        return result

    for j in range(len(zs)-1):
        for i in range(len(ys)-1):
            a,b,c,d = grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]
            triangles = [[a,b,c],[a,c,d]] if i>=90 else [[a,b,d],[b,c,d]]
            for triangle in triangles:
                poly = clipped(clipped(triangle,1),-1)
                ids = [vertex(p) for p in poly]
                for k in range(1,len(ids)-1):
                    face = [ids[0],ids[k],ids[k+1]]
                    if len(set(face)) == 3:
                        faces.append(face)
    colors = [list(map(int, TEAL if p[1]>=0 else GOLD)) for p in vertices]
    normals = [np.round(normal(p[1],p[2]),7).tolist() for p in vertices]
    axis = sorted([i for i,p in enumerate(vertices) if p[0]==0 and p[1]==0], key=lambda i:vertices[i][2])
    return dict(name='pitchfork-surface',kind='pitchfork-schematic',status='schematic',
        vertices=vertices,faces=faces,paths=[axis],normals=normals,vertexColors=colors,
        halfWidth=math.pi,bounds=dict(x=LIMIT,zMin=ZMIN,zMax=ZMAX),
        view=dict(yaw=.64,pitch=.35,radius=7),
        description='Original qualitative drawing of the w=pi pitchfork. Not a numerical translator solution.',
        drawingMap='(x,y,z) = (0.5 sin(y) exp(z) + yz - tan(y/2), y, z)',
        source='Hoffman-Martin-White, arXiv:1903.04617v4, Figures 6 and 14, Theorem 12.1.')


def write_static(data):
    width,height = 1200,710
    image = Image.new('RGB',(width*2,height*2),'#f7fafb')
    draw = ImageDraw.Draw(image)
    v,f = np.array(data['vertices']),np.array(data['faces'])
    yaw,pitch = .64,.35
    rot = np.array([[math.cos(yaw),-math.sin(yaw),0],
        [-math.sin(yaw)*math.sin(pitch),-math.cos(yaw)*math.sin(pitch),math.cos(pitch)],
        [math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)]])
    q = v@rot.T
    scale = 50
    screen = np.column_stack([width/2+scale*q[:,0],height/2+20-scale*q[:,1]])*2
    normals = np.array(data['normals'])@rot.T
    light = np.array([-.35,.55,.8]);light /= np.linalg.norm(light)
    colors = np.array(data['vertexColors'])
    for i in np.argsort(q[f,2].mean(axis=1)):
        face = f[i];n = normals[face].mean(axis=0);n /= np.linalg.norm(n)
        if n[2] < 0:n = -n
        bright = .5+.48*max(0,float(n@light))
        color = tuple(np.clip(colors[face].mean(axis=0)*bright,0,255).astype(int))
        pts = [tuple(p) for p in screen[face]]
        draw.polygon(pts, fill=color)
        # Sparse parameter lines, depth ordered with their incident triangles.
        for a,b in zip(face,np.roll(face,-1)):
            if abs(v[a,2]-v[b,2])<1e-7 and abs((v[a,2]-ZMIN)/.5-round((v[a,2]-ZMIN)/.5))<1e-5:
                draw.line([tuple(screen[a]),tuple(screen[b])],fill=tuple(int(c*.63) for c in color),width=1)
    image = image.resize((width,height),Image.Resampling.LANCZOS)
    buf = io.BytesIO();image.save(buf,format='PNG')
    png = base64.b64encode(buf.getvalue()).decode()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img" aria-labelledby="title desc">
<title id="title">Pitchfork: two graphical halves joined along a vertical line</title>
<desc id="desc">Original schematic for half-width pi, reflected to upward translation. Teal and ochre halves form one smooth surface. Not a solved translator. Artificial window edges are shown.</desc>
<rect width="1200" height="800" fill="#f7fafb"/>
<image x="0" y="45" width="1200" height="710" href="data:image/png;base64,{png}"/>
<g font-family="system-ui,sans-serif" fill="#274b5a">
<text x="38" y="36" font-size="23">Pitchfork · half-width w = π</text>
<text x="38" y="65" font-size="16">Source-informed schematic · upward translation</text>
<path d="M1120 140V82m-7 11 7-11 7 11" fill="none" stroke="#274b5a" stroke-width="2"/>
<text x="1134" y="115" font-size="20">z</text>
<circle cx="44" cy="763" r="7" fill="#42919e"/><text x="60" y="769" font-size="17">Graph over 0 &lt; y &lt; π</text>
<circle cx="330" cy="763" r="7" fill="#d3934f"/><text x="346" y="769" font-size="17">Its half-turn about the z-axis</text>
<text x="38" y="796" font-size="15">Hoffman–Martín–White, Figures 6 and 14, Theorem 12.1. This drawing does not solve the translator equation.</text>
</g></svg>'''
    (OUT/'pitchfork-surface.svg').write_text(svg)


if __name__=='__main__':
    data = make_surface()
    (OUT/'pitchfork-surface.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    write_static(data)
    print(f"Pitchfork schematic: {len(data['vertices'])} vertices, {len(data['faces'])} triangles")
