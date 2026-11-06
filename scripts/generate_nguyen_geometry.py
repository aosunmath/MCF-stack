"""Nguyen sphere–plane construction picture, not a solved self-shrinker.

Source: arXiv:1106.5272v3, pp. 7–13. See documentation/nguyen-picture.md.
Regeneration needs NumPy, scikit-image, fast-simplification, and Pillow.
"""
from pathlib import Path
import base64
import io
import json
import numpy as np
from skimage.measure import marching_cubes
import fast_simplification
from PIL import Image, ImageDraw

# Generic mesh operations only; no identification of the two shrinker families.
from generate_kkm_geometry import clip_disk, topology

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
COUNTS = [6, 10, 14]
COLORS = np.array([[83, 145, 173], [207, 131, 75], [104, 169, 157]])


def smooth(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)


def colors_for(vertices, local=False):
    if local:
        # Display coordinates (y,x,z) have the periodic axis horizontal.
        x, z = vertices[:, 1], vertices[:, 2]
        plane = smooth((np.abs(x)-.6)/.8)
        core = 1-smooth((np.maximum(np.abs(x), np.abs(z))-.45)/.9)
    else:
        r = np.linalg.norm(vertices[:, :2], axis=1)
        plane = (smooth((r-2.3)/.5) + (1-smooth((r-1.3)/.4)))*(1-smooth((np.abs(vertices[:, 2])-.25)/.45))
        core = smooth((.85-np.abs(vertices[:, 2]))/.5)*smooth((.65-np.abs(r-2))/.4)
    rgb = (1-plane[:, None])*COLORS[0]+plane[:, None]*COLORS[2]
    return np.rint((1-core[:, None])*rgb+core[:, None]*COLORS[1]).astype(int).tolist()


def make_surface(m):
    # sin(y) = sinh(x) sinh(z), with y=m theta. Our global drawing map
    # r=2 exp(x/m) sech(z/m), h=2 tanh(z/m) closes the vertical wings
    # into caps. It agrees to first order with the normalized wrapping
    # map at the equator, but is not Nguyen's ODE/cutoff construction.
    axis = np.linspace(-3.95, 3.95, 221)
    height = np.linspace(-2.12, 2.12, 132)
    X, Y, H = np.meshgrid(axis, axis, height, indexing='ij', sparse=True)
    r = np.sqrt(X*X+Y*Y)
    z = m*np.arctanh(np.clip(H/2, -.99999999, .99999999))
    x = m*np.log(np.maximum(r, 1e-12)/2/np.sqrt(np.maximum(1-(H/2)**2, 1e-16)))
    field = np.tanh(x)*np.tanh(z)-np.sin(m*np.arctan2(Y, X))/np.cosh(np.clip(x, -100, 100))/np.cosh(z)
    field = np.where(np.abs(H) >= 2, np.sign(H), field)
    v, f, _, _ = marching_cubes(field.astype(np.float32), 0,
        spacing=(axis[1]-axis[0], axis[1]-axis[0], height[1]-height[0]), allow_degenerate=False)
    v += [axis[0], axis[0], height[0]]
    v, f = fast_simplification.simplify(v, f, target_count=24000, agg=5)
    v, f = clip_disk(v, f, 3.65)
    colors = colors_for(v)
    # A freely chosen conical profile, not the paper's unknown phi(theta).
    r = np.linalg.norm(v[:, :2], axis=1)
    t = np.clip((r-2.35)/.85, 0, 1)
    v[:, 2] += .055*r*np.sin(m*np.arctan2(v[:, 1], v[:, 0]))*t**3*(10-15*t+6*t*t)
    audit = topology(v, f)
    assert audit['components'] == 1 and audit['boundary_loops'] == 1, audit
    assert audit['boundary_is_manifold'] and audit['edge_incidence'] == [1, 2], audit
    assert audit['genus'] == m-1, audit
    data = dict(name='nguyen-m-saddles', kind='nguyen-scherk-schematic', status='schematic',
        m=m, genus=m-1, vertices=np.round(v, 7).tolist(), faces=f.tolist(), paths=[],
        vertexColors=colors, view=dict(yaw=.38, pitch=.33, radius=3.8),
        description='Connected sphere–plane construction schematic informed by Nguyen Part III. '
                    'Not a solved shrinker or a certified approximation.',
        construction=dict(base_radius=2, display_radius=3.65, end_amplitude=.055,
                          scherk_equation='sin(y) = sinh(x) sinh(z)'))
    return data, audit


def make_scherk():
    # Two periods of the exact minimal ingredient, sampled and triangulated.
    a = np.linspace(-2.15, 2.15, 88)
    b = np.linspace(-2*np.pi, 2*np.pi, 249)
    x, y, z = np.meshgrid(a, b, a, indexing='ij', sparse=True)
    field = np.sin(y)-np.sinh(x)*np.sinh(z)
    v, f, _, _ = marching_cubes(field.astype(np.float32), 0,
        spacing=(a[1]-a[0], b[1]-b[0], a[1]-a[0]), allow_degenerate=False)
    v += [a[0], b[0], a[0]]
    v, f = fast_simplification.simplify(v, f, target_count=18000, agg=5)
    for _ in range(5):
        x, y, z = v.T
        residual = np.sin(y)-np.sinh(x)*np.sinh(z)
        gradient = np.column_stack([-np.cosh(x)*np.sinh(z), np.cos(y), -np.sinh(x)*np.cosh(z)])
        v -= residual[:, None]*gradient/np.sum(gradient**2, axis=1)[:, None]
    # Swap horizontal axes for an easily read unwrapped strip.
    v = np.round(v[:, [1, 0, 2]], 7); f = f[:, ::-1]
    residual = np.abs(np.sin(v[:, 0])-np.sinh(v[:, 1])*np.sinh(v[:, 2]))
    data = dict(name='nguyen-scherk-detail', kind='nguyen-scherk-detail', status='exact-ingredient-mesh',
        vertices=v.tolist(), faces=f.tolist(), paths=[], vertexColors=colors_for(v, local=True),
        view=dict(yaw=.12, pitch=.46, radius=6.7),
        description='Finite triangulation of sin(y)=sinh(x)sinh(z), with display axes (y,x,z). '
                    'An exact minimal ingredient; not the completed shrinker.')
    return data, dict(vertices=len(v), faces=len(f), max_vertex_equation_residual=float(residual.max()))


def render_view(painter, data, center, scale, yaw, pitch, cut=False):
    v = np.array(data['vertices']); f = np.array(data['faces'])
    colors = np.array(data['vertexColors'])
    x, y, z = v.T
    a = x*np.cos(yaw)-y*np.sin(yaw); b = x*np.sin(yaw)+y*np.cos(yaw)
    q = np.column_stack([a, z*np.cos(pitch)-b*np.sin(pitch), z*np.sin(pitch)+b*np.cos(pitch)])
    xy = np.column_stack([center[0]+scale*q[:, 0], center[1]-scale*q[:, 1]])
    def clip(poly, normal):
        result = []
        for a, b in zip(poly, poly[1:]+poly[:1]):
            da, db = a[:2]@normal, b[:2]@normal
            if da <= 0: result.append(a)
            if da*db < 0: result.append(a+(b-a)*da/(da-db))
        return result
    for j in np.argsort(q[f, 2].mean(axis=1)):
        face = f[j]; a, b, c = q[face]
        n = np.cross(b-a, c-a); n /= np.linalg.norm(n)
        if n[2] < 0: n = -n
        light = .50+.48*max(0, n@np.array([-.35, .55, .76]))
        rgb = tuple(np.rint(colors[face].mean(axis=0)*light).astype(int))+(255,)
        if cut:
            polygons = [clip(clip(list(v[face]), np.array([-side, 0])), np.array([-.35*side, 1])) for side in [-1, 1]]
            for poly in polygons:
                if len(poly) < 3: continue
                p = np.array(poly); x, y, z = p.T
                a = x*np.cos(yaw)-y*np.sin(yaw); b = x*np.sin(yaw)+y*np.cos(yaw)
                screen = np.column_stack([center[0]+scale*a, center[1]-scale*(z*np.cos(pitch)-b*np.sin(pitch))])
                painter.polygon([tuple(np.rint(3*p).astype(int)) for p in screen], fill=rgb)
        else:
            painter.polygon([tuple(np.rint(3*p).astype(int)) for p in xy[face]], fill=rgb)


def drawing(surface, scherk):
    image = Image.new('RGBA', (3300, 2700)); painter = ImageDraw.Draw(image)
    render_view(painter, surface, (275, 295), 65, .38, .33)
    render_view(painter, surface, (825, 295), 65, .38, .48, True)
    render_view(painter, scherk, (285, 677), 30, .12, .46)
    buffer = io.BytesIO()
    image.resize((2200, 1800), Image.Resampling.LANCZOS).save(buffer, format='PNG', optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 900" role="img" aria-labelledby="title desc">',
        '<title id="title">Nguyen’s shrinking saddles: sphere–plane desingularization</title>',
        '<desc id="desc">A connected construction schematic and cutaway expose two caps, an inner disk, and one outer sheet joined by a Scherk saddle belt. Below is an unwrapped Scherk minimal surface. The global picture is not a solved shrinker.</desc>',
        '<rect width="1100" height="900" fill="#f7fafb"/>',
        f'<image width="1100" height="900" href="data:image/png;base64,{encoded}"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        '<text x="38" y="47" font-size="28" font-weight="600">Nguyen’s one-ended shrinking saddles</text>',
        '<text x="38" y="79" font-size="18" fill="#58727e">One connected surface: spherical caps + inner disk + exterior, joined through a Scherk belt</text>',
        '<text x="275" y="480" text-anchor="middle" font-size="19" font-weight="600">Full construction schematic</text>',
        '<text x="825" y="480" text-anchor="middle" font-size="19" font-weight="600">Cutaway exposes the inner disk and lower cap</text>',
        '<circle cx="48" cy="514" r="6" fill="#5391ad"/><text x="64" y="520" font-size="17">Two caps</text>',
        '<circle cx="251" cy="514" r="6" fill="#cf834b"/><text x="267" y="520" font-size="17">Scherk saddle belt</text>',
        '<circle cx="539" cy="514" r="6" fill="#68a99d"/><text x="555" y="520" font-size="17">Inner disk / one outer sheet</text>',
        '<path d="M38 547H1062" stroke="#cfdee4"/>',
        '<text x="38" y="580" font-size="18" font-weight="600">The local ingredient, unwrapped</text>',
        '<text x="285" y="770" text-anchor="middle" font-size="17">sin y = sinh x sinh z · two periods in y</text>',
        '<text x="590" y="595" font-size="18" font-weight="600">Four wings of each Scherk period</text>',
        '<text x="590" y="628" font-size="17">z → ±∞: upper and lower spherical caps</text>',
        '<text x="590" y="658" font-size="17">x → −∞: inner disk</text>',
        '<text x="590" y="688" font-size="17">x → +∞: exterior sheet, continuing to one end</text>',
        '<text x="590" y="728" font-size="17">Wrap m periods around the equator: genus m − 1.</text>',
        '<text x="590" y="758" font-size="16" fill="#58727e">Shown: m = 10, model genus 9; no small-m existence claim.</text>',
        '<path d="M38 795H1062" stroke="#cfdee4"/>',
        '<text x="38" y="829" font-size="17">The completed shrinker has one conical end. The cone drawn here is chosen for illustration.</text>',
        '<text x="38" y="861" font-size="17" font-weight="600">CONSTRUCTION SCHEMATIC · not a solved shrinker · all visible outer and cut edges are artificial</text>',
        '</g></svg>']
    (OUT/'nguyen-m-saddles.svg').write_text('\n'.join(parts)+'\n')


def main():
    audits = {}
    scherk, scherk_audit = make_scherk()
    (OUT/'nguyen-scherk-detail.json').write_text(json.dumps(scherk, separators=(',', ':'))+'\n')
    for m in COUNTS:
        data, audits[str(m)] = make_surface(m)
        name = 'nguyen-m-saddles' if m == 10 else f'nguyen-m-saddles-{m}'
        (OUT/(name+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
        if m == 10: drawing(data, scherk)
    audit = dict(status='schematic', source='https://arxiv.org/pdf/1106.5272v3',
        source_locations='Theorem 1; Section 2, pp. 7–9; Definition 13 and Proposition 14; Definition 21',
        grid=[221, 221, 132], models=audits, scherk_detail=scherk_audit)
    (OUT/'nguyen-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__': main()
