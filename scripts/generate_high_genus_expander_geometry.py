"""Original topology model for HMW expanders, NOT a solution of the expander PDE.

Read documentation/high-genus-expander-picture.md before interpreting this mesh.
Requires NumPy, scikit-image, fast-simplification and Pillow.
"""
from pathlib import Path
import base64
import io
import json
import numpy as np
from skimage.measure import marching_cubes
import fast_simplification
from PIL import Image, ImageDraw
from generate_kkm_geometry import clip_disk, topology
from generate_nguyen_geometry import render_view

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
COUNTS = [4, 12, 20]
COLORS = np.array([[76, 142, 173], [218, 155, 87], [90, 166, 147]])


def smooth(t):
    t = np.clip(t, 0, 1)
    return t**3*(10-15*t+6*t*t)


def coefficients(r, theta, m):
    # A cubic with one central sheet and three exterior sheets. Angular
    # oscillations connect them through 2m saddle regions. This is a drawing
    # construction, not HMW's degree-theoretic construction.
    outer = smooth((r-2.65)/.45)
    a = .15*(r*r-2.1**2*(1-outer))
    b = .12*np.exp(-((r-2.1)/.45)**2)*np.minimum(r/1.4, 1)**m
    b *= (1-outer)*np.cos(m*theta)
    return a, b


def end_shear(r, theta):
    # The same G_4-symmetric, nonrotational cone for every displayed genus.
    return .035*r*np.cos(4*theta)*smooth((r-2.4)/.7)


def make_surface(m):
    axis = np.linspace(-3.7, 3.7, 221)
    height = np.linspace(-2, 2, 150)
    x, y, z = np.meshgrid(axis, axis, height, indexing='ij', sparse=True)
    r = np.sqrt(x*x+y*y); theta = np.arctan2(y, x)
    a, b = coefficients(r, theta, m)
    v, f, _, _ = marching_cubes((z**3-a*z+b).astype(np.float32), 0,
        spacing=(axis[1]-axis[0], axis[1]-axis[0], height[1]-height[0]),
        allow_degenerate=False)
    v += [axis[0], axis[0], height[0]]
    v, f = fast_simplification.simplify(v, f, target_count=26000, agg=5)
    v, f = clip_disk(v, f, 3.5)
    # Save the shear separately: changing type reverses the core but preserves
    # the same exterior set, including its nonrotational middle sheet.
    r = np.linalg.norm(v[:, :2], axis=1)
    theta = np.arctan2(v[:, 1], v[:, 0])
    shear = end_shear(r, theta)
    v[:, 2] *= .72
    level = np.clip(v[:, 2]/(.72*np.sqrt(.15)*np.maximum(r, .01)), -1, 1)
    base = np.where((level >= 0)[:, None],
        (1-level[:, None])*COLORS[1]+level[:, None]*COLORS[0],
        (1+level[:, None])*COLORS[1]-level[:, None]*COLORS[2])
    audit = topology(v, f)
    assert audit['components'] == 1 and audit['boundary_loops'] == 3, audit
    assert audit['boundary_is_manifold'] and audit['edge_incidence'] == [1, 2], audit
    assert audit['genus'] == m-1, audit
    data = dict(name='high-genus-expanders', kind='high-genus-expander-schematic',
        status='schematic', k=4, m=m, genus=m-1,
        vertices=np.round(v, 7).tolist(), faces=f.tolist(), paths=[],
        endShear=np.round(shear, 7).tolist(), vertexColors=np.rint(base).astype(int).tolist(),
        view=dict(yaw=.38, pitch=.30, radius=3.7),
        description='Connected topology model with three conical ends. Not an HMW expander '
                    'or a numerical approximation to one. k=4 is an illustrative count only.',
        cone=dict(k=4, slope=float(.72*np.sqrt(.15)), wave=.035),
        source=dict(url='https://arxiv.org/abs/2605.09657v1',
                    locators='Theorems 1.1–1.2, Definition 3.1 and Figure 1, Definition 4.1, '
                             'Theorem 5.1, Sections 9–10, Theorems 12.6–12.7'))
    return data, audit


def cone_model():
    v, f, colors = [], [], []
    for sheet, color in zip([1, 0, -1], COLORS):
        start = len(v)
        for j in range(25):
            r = .02+(3.5-.02)*j/24
            for i in range(160):
                t = 2*np.pi*i/160
                v.append([r*np.cos(t), r*np.sin(t), r*(sheet*.72*np.sqrt(.15)+.035*np.cos(4*t))])
                colors.append(color.tolist())
        for j in range(24):
            for i in range(160):
                a = start+j*160+i; b = start+j*160+(i+1)%160
                f += [[a, b, b+160], [a, b+160, a+160]]
    return dict(vertices=v, faces=f, paths=[], vertexColors=colors)


def drawing(data):
    # Rasterize the mesh once; SVG retains crisp, accessible explanatory text.
    image = Image.new('RGBA', (3000, 2520)); painter = ImageDraw.Draw(image)
    surface = {**data, 'vertices':[[x, y, z+s] for (x, y, z), s in zip(data['vertices'], data['endShear'])]}
    render_view(painter, surface, (255, 248), 61, .38, .30)
    render_view(painter, surface, (745, 248), 61, .38, .43, True)
    buffer = io.BytesIO()
    image.resize((2000, 1680), Image.Resampling.LANCZOS).save(buffer, format='PNG', optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 840" role="img" aria-labelledby="title desc">',
         '<title id="title">Three conical ends, connected through a core with handles</title>',
         '<desc id="desc">Original connected topology model and cutaway, with genus 3 and three ends. '
         'Two reflection-slice diagrams explain type 1 and type 2. These are illustrations of topology, '
         'not computed self-expanders; the cone is chosen for display.</desc>',
         '<rect width="1000" height="840" fill="#f7fafb"/>',
         f'<image width="1000" height="840" href="data:image/png;base64,{encoded}"/>',
         '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">']
    def text(x, y, words, size=18, weight=400, anchor='start', color='#183f52'):
        s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{words}</text>')
    text(32, 42, 'One fixed cone; many possible genera', 28, 600)
    text(32, 73, 'Hoffman–Martín–White · three-ended surfaces in ℝ³ · topology model', 18, color='#526b77')
    text(255, 392, 'Connected model', 20, 600, 'middle')
    text(745, 392, 'Cutaway reveals the joining region', 20, 600, 'middle')
    text(500, 423, 'Shown: k = 4, a = 0, model genus 3. These small counts carry no existence claim.', 16, anchor='middle', color='#526b77')
    for x, color, words in [(45, '#4c8ead', 'Upper end'), (265, '#da9b57', 'Middle end'), (485, '#5aa693', 'Lower end')]:
        s.append(f'<circle cx="{x}" cy="453" r="6" fill="{color}"/>'); text(x+15, 459, words, 17)
    text(700, 459, 'All three wrap around the z-axis.', 16)
    s.append('<path d="M32 482H968" stroke="#d3e2e8"/>')
    text(32, 514, 'The reflection slice distinguishes two types', 20, 600)
    # Original half-slice drawings: just the endpoint pairing, no metric claim.
    for x, kind in [(48, 1), (380, 2)]:
        text(x, 548, f'Type {kind}', 19, 600)
        if kind == 1:
            d=f'M{x+235} 572 C{x+112} 572 {x+112} 624 {x+235} 624'
            other=f'M{x+25} 639 C{x+70} 646 {x+118} 676 {x+235} 676'
        else:
            d=f'M{x+235} 624 C{x+112} 624 {x+112} 676 {x+235} 676'
            other=f'M{x+25} 609 C{x+70} 600 {x+118} 572 {x+235} 572'
        s.append(f'<path d="{other}" fill="none" stroke="#899da6" stroke-width="3"/>')
        s.append(f'<path d="{d}" fill="none" stroke="#21667f" stroke-width="4"/>')
        for y, name in [(572,'upper'),(624,'middle'),(676,'lower')]:
            s.append(f'<circle cx="{x+235}" cy="{y}" r="4" fill="#21667f"/>'); text(x+248, y+5, name, 14)
        text(x+150, 707, 'middle ↔ '+('upper' if kind==1 else 'lower'), 17, anchor='middle')
    text(735, 548, 'For each permitted genus:', 16, 600)
    text(735, 583, 'type 1: small + big', 17)
    text(735, 613, 'type 2: small + big', 17)
    text(735, 652, '“Size” is a weighted local', 15, color='#526b77')
    text(735, 675, 'area test, not zoom or scale.', 15, color='#526b77')
    s.append('<path d="M32 730H968" stroke="#d3e2e8"/>')
    text(32, 763, 'Theorem: g = pᵃk − 1, with p odd prime, a ≥ 0 and one suitable cone held fixed.', 18)
    text(32, 795, 'SCHEMATIC · no expander PDE is solved · ends and cut edges are truncated for display', 16, 600)
    text(32, 822, 'Source: arXiv:2605.09657v1, Definitions 3.1 and 4.1, Figure 1, Theorems 1.2 and 5.1.', 14, color='#526b77')
    s.append('</g></svg>')
    (OUT/'high-genus-expanders.svg').write_text('\n'.join(s)+'\n')


def main():
    audits = {}
    for m in COUNTS:
        data, audit = make_surface(m)
        if m == 4:
            data['coneMesh'] = cone_model()
            drawing(data)
        suffix = '' if m == 4 else f'-{m}'
        (OUT/f'high-genus-expanders{suffix}.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
        audits[str(m)] = audit
        print(m, audit, flush=True)
    (OUT/'high-genus-expanders-audit.json').write_text(json.dumps(audits, indent=2)+'\n')


if __name__ == '__main__':
    main()
