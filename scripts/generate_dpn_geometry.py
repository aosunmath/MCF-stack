"""Dávila–del Pino–Nguyen construction drawing, not a solved translator.

Read documentation/finite-genus-translator-picture.md. Regeneration requires
NumPy, SciPy, scikit-image, fast-simplification and Pillow. ODE ingredients
have unit upward speed. The implicit tunnel interpolation is illustrative.
"""
from pathlib import Path
from functools import lru_cache
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from skimage.measure import marching_cubes
import fast_simplification
from generate_kkm_geometry import topology

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
R, RHO, ZMAX = 1., 1.4, 4.4
COUNTS = [8, 12, 16]
COLORS = np.array([[77, 143, 174], [97, 166, 151], [220, 153, 79]])


@lru_cache
def profiles(tolerance=1e-10):
    r0 = 1e-5
    bowl = solve_ivp(lambda r, y: [y[1], (1+y[1]**2)*(1-y[1]/r)],
        (r0, 7), [r0*r0/4, r0/2], dense_output=True, rtol=tolerance, atol=tolerance*.1)
    def rhs(s, y):
        r, z, a = y
        return [np.cos(a), np.sin(a), np.cos(a)-np.sin(a)/r]
    def stop(s, y): return y[0]-7
    stop.terminal = True
    curves = []
    for a in [np.pi/2, -np.pi/2]:
        sol = solve_ivp(rhs, (0, 80), [R, 0, a], events=stop,
            max_step=.006, rtol=tolerance, atol=tolerance*.1, dense_output=True)
        curves.append(sol)
    wings = [PchipInterpolator(s.y[0], s.y[1]) for s in curves]
    shift = float(bowl.sol(RHO)[0]-wings[1](RHO))
    return bowl, wings, curves, shift


def fields(r, z):
    bowl, wings, _, shift = profiles()
    rb = np.maximum(r, 1e-5)
    b, slope = bowl.sol(rb.ravel()).reshape(2, *rb.shape)
    b = np.where(r < 1e-5, r*r/4, b)
    rc = np.maximum(r, R)
    upper, lower = [w(rc)+shift for w in wings]
    mid = (upper+lower)/2
    gap2 = ((upper-lower)/2)**2
    # The squared wing separation extends smoothly through the vertical neck:
    # z-z_neck ~ +/-sqrt(2 R (r-R)), hence gap^2 ~ 2 R (r-R).
    gap2 = np.where(r < R, 2*R*(r-R), gap2)
    c = (z-mid)**2-gap2
    # Fixed positive normalization at the crossing; no zero set is changed.
    crossing_gap = float(wings[0](RHO)-wings[1](RHO))
    crossing_slope = float(wings[1].derivative()(RHO))
    cnorm = crossing_gap*np.sqrt(1+crossing_slope**2)
    return (z-b)/np.sqrt(1+slope**2), c/cnorm


def make_model(m):
    # A bent Scherk-type interpolation in two defining functions. These
    # oblique coordinates are NOT isometric Scherk coordinates; no PDE
    # residual claim is made. Its zero set approaches the ODE ingredients.
    axis = np.linspace(-4.55, 4.55, 263)
    heights = np.linspace(-.6, ZMAX, 172)
    X, Y, Z = np.meshgrid(axis, axis, heights, indexing='ij', sparse=True)
    r = np.sqrt(X*X+Y*Y)
    b, c = fields(r, Z)
    h = RHO/m*.78
    u, v = b/h, c/h
    wave = np.cos(m*np.arctan2(Y, X))
    # Make the field independent of angle near the rotation axis.
    cutoff = np.clip((r-.65)/.25, 0, 1)
    cutoff = cutoff*cutoff*(3-2*cutoff)
    field = np.tanh(u)*np.tanh(v)-wave*cutoff/np.cosh(np.clip(u, -70, 70))/np.cosh(np.clip(v, -70, 70))
    vertices, faces, _, _ = marching_cubes(field.astype(np.float32), 0,
        spacing=(axis[1]-axis[0], axis[1]-axis[0], heights[1]-heights[0]), allow_degenerate=False)
    vertices += [axis[0], axis[0], heights[0]]
    vertices, faces = fast_simplification.simplify(vertices, faces, target_count=28000, agg=5)
    audit = topology(vertices, faces)
    assert audit['components'] == 1 and audit['boundary_loops'] == 3, audit
    assert audit['edge_incidence'] == [1, 2] and audit['boundary_is_manifold'], audit
    assert audit['genus'] == m-1, audit
    # All three boundary loops must lie at the artificial height cutoff.
    assert np.max(np.linalg.norm(vertices[:, :2], axis=1)) < axis[-1]-.05
    r = np.linalg.norm(vertices[:, :2], axis=1)
    b, c = fields(r, vertices[:, 2])
    bowl_weight = np.abs(c)/(np.abs(b)+np.abs(c)+1e-10)
    rgb = bowl_weight[:, None]*COLORS[0]+(1-bowl_weight[:, None])*COLORS[1]
    core = np.exp(-((r-RHO)/.26)**4-((vertices[:, 2]-profiles()[0].sol(RHO)[0])/.4)**4)
    rgb = (1-core[:, None])*rgb+core[:, None]*COLORS[2]
    data = dict(name='bowl-catenoid-gluing', kind='dpn-construction', status='schematic',
        m=m, modelGenus=m-1, vertices=np.round(vertices, 7).tolist(), faces=faces.tolist(), paths=[],
        vertexColors=np.rint(rgb).astype(int).tolist(), view=dict(yaw=0, pitch=.42, radius=4.4, centerZ=1.9),
        description='Connected drawing with three upward ends and a Scherk-type tunnel belt. Not a solved translator.',
        construction=dict(neckRadius=R, intersectionRadius=RHO, displayHeight=ZMAX,
                          smoothingScale=h, equation='sinh(B/h) sinh(C/h) = cutoff(r) cos(m theta)'),
        audit=audit)
    return data


def make_input():
    bowl, wings, curves, shift = profiles()
    meridians = []
    r = np.linspace(0, 4.5, 240)
    z = bowl.sol(np.maximum(r, 1e-5))[0]; z[0] = 0
    meridians.append(np.column_stack([r, z]).tolist())
    for curve in curves:
        s = np.linspace(0, curve.t[-1], 800)
        p = curve.sol(s)
        meridians.append(np.column_stack([p[0], p[1]+shift]).tolist())
    # Crop each outward profile at the same height, interpolating the rim.
    for i, profile in enumerate(meridians):
        a = np.array(profile); k = np.flatnonzero(a[:, 1] > ZMAX)[0]
        t = (ZMAX-a[k-1, 1])/(a[k, 1]-a[k-1, 1])
        meridians[i] = np.vstack([a[:k], a[k-1]+t*(a[k]-a[k-1])]).tolist()
    vertices, faces, groups = [], [], []
    segments = 128
    for group, profile in enumerate(meridians):
        start = len(vertices)
        for r, z in profile:
            vertices.extend([[r*np.cos(a), r*np.sin(a), z] for a in np.arange(segments)*2*np.pi/segments])
        for i in range(len(profile)-1):
            for j in range(segments):
                a = start+i*segments+j; b = start+i*segments+(j+1)%segments
                faces.extend([[a, b, b+segments], [a, b+segments, a+segments]])
                groups.extend([0 if group==0 else 1]*2)
    # Lightweight display decimation; original meridians are retained.
    v, f = fast_simplification.simplify(np.array(vertices), np.array(faces), target_count=20000, agg=5)
    r = np.linalg.norm(v[:, :2], axis=1); b, c = fields(r, v[:, 2])
    colors = [COLORS[0 if abs(x)<abs(y) else 1].astype(int).tolist() for x,y in zip(b,c)]
    return dict(name='dpn-bowl-catenoid-input',kind='dpn-input',status='numerical-ode',
        vertices=np.round(v,7).tolist(), faces=f.tolist(), paths=[], vertexColors=colors,
        meridians=meridians, intersection=[RHO,float(bowl.sol(RHO)[0])],
        view=dict(yaw=0,pitch=.42,radius=4.4,centerZ=1.9),
        description='Numerically integrated bowl and winglike translator, before desingularization.',
        normalization='Hvec = e_z perpendicular; unit upward speed',
        parameters=dict(neckRadius=R,neckHeight=shift,intersectionRadius=RHO,displayHeight=ZMAX),
        source=dict(url='https://doi.org/10.1016/j.aim.2017.09.014',locators='Theorem 1.1; Fig. 2; equations (2.1), (2.3)'))


def drawings():
    # Original rasterization of our computed mesh; no source figure is copied.
    from PIL import Image, ImageDraw
    import base64
    import io
    from generate_nguyen_geometry import render_view
    data = json.loads((OUT/'bowl-catenoid-gluing.json').read_text())
    image = Image.new('RGBA', (3300, 2160)); painter = ImageDraw.Draw(image)
    shifted = dict(data, vertices=(np.array(data['vertices'])-[0,0,1.9]).tolist())
    render_view(painter, shifted, (310, 370), 53, 0, .42, True)
    detail = Image.new('RGBA', (1290, 1140)); dp = ImageDraw.Draw(detail)
    shifted = dict(data, vertices=(np.array(data['vertices'])-[0,0,.65]).tolist())
    render_view(dp, shifted, (215, 210), 110, 0, .18, True)
    image.alpha_composite(detail, (1950, 390))
    buffer = io.BytesIO(); image.resize((2200,1440), Image.Resampling.LANCZOS).save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="720" viewBox="0 0 1100 720" role="img" aria-labelledby="title desc">
<title id="title">Three-ended translator: a ring of tunnels</title>
<desc id="desc">Original connected construction schematic based on Dávila, del Pino and Nguyen. A cutaway reveals a bowl sheet and the two catenoid sheets joined through a gold tunnel belt. An enlargement shows the tunnels. This is not a solved translator.</desc>
<rect width="1100" height="720" fill="#f7fafb"/>
<image width="1100" height="720" href="data:image/png;base64,{encoded}"/>
<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">
<text x="34" y="45" font-size="28" font-weight="600">Three ends joined through a ring of tunnels</text>
<text x="34" y="78" font-size="18" fill="#58727e">Dávila–del Pino–Nguyen · original construction schematic</text>
<text x="34" y="119" font-size="18" font-weight="600">Cutaway: three upward ends</text>
<text x="660" y="119" font-size="18" font-weight="600">The joining region, enlarged</text>
<rect x="650" y="510" width="430" height="74" fill="#f7fafb"/>
<text x="670" y="542" font-size="17">A Scherk-like belt replaces the crossing.</text>
<text x="670" y="568" font-size="16" fill="#58727e">12 illustrative periods; model genus 11</text>
<path d="M34 596H1066" stroke="#cfdee4"/>
<circle cx="44" cy="627" r="6" fill="#4d8fae"/><text x="60" y="633" font-size="17">Bowl sheet</text>
<circle cx="300" cy="627" r="6" fill="#61a697"/><text x="316" y="633" font-size="17">Two catenoid sheets</text>
<circle cx="650" cy="627" r="6" fill="#dc994f"/><text x="666" y="633" font-size="17">Tunnel belt</text>
<text x="34" y="674" font-size="17" font-weight="600">SCHEMATIC · not a solved translator · rims and cut edges are display boundaries</text>
<text x="34" y="702" font-size="16" fill="#58727e">The theorem requires large genus; the displayed period counts are illustrative.</text>
</g></svg>'''
    (OUT/'bowl-catenoid-gluing.svg').write_text(svg+'\n')
    # Exact numerical input profiles in equal r,z units, with all three end labels.
    data = json.loads((OUT/'dpn-bowl-catenoid-input.json').read_text())
    # Use equal units to preserve intersection angles (fit 4.4 by 4.4).
    def screen(p): return (83+48*p[0], 315-48*p[1])
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc">',
        '<title id="title">Numerical meridians of the bowl and translating catenoid</title>',
        '<desc id="desc">The blue bowl and green two-wing catenoid cross on the lower wing at radius 1.4. Rotation about the vertical axis gives one intersection circle. All three ends rise upward. Equal units are used on both axes.</desc>',
        '<rect width="640" height="410" fill="#f7fafb"/><g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        '<text x="26" y="34" font-size="21" font-weight="600">The numerical input, before gluing</text>',
        '<text x="26" y="61" font-size="14" fill="#58727e">Unit upward speed · equal axis scales · equations (2.1), (2.3)</text>',
        '<path d="M83 88V330M67 315H313" stroke="#9aadb5" fill="none"/>',
        '<text x="66" y="90" font-size="14">z</text><text x="320" y="321" font-size="14">r</text>']
    for i, curve in enumerate(data['meridians']):
        color = '#4d8fae' if i==0 else '#459481'
        points = ' '.join(f'{x:.2f},{y:.2f}' for x,y in map(screen,curve))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.6"/>')
        x,y=screen(curve[-1]);label=['Bowl end','Upper catenoid end','Lower catenoid end'][i]
        ty=[130,99,160][i]
        parts.append(f'<path d="M{x:.2f} {y:.2f}L345 {ty-5}" fill="none" stroke="{color}"/><text x="357" y="{ty}" font-size="14" fill="{color}">{label}</text>')
    x,y=screen(data['intersection'])
    parts += [f'<circle cx="{x}" cy="{y}" r="4.5" fill="#bd7131" stroke="white"/>',
        f'<path d="M{x+6} {y}L345 239" stroke="#bd7131" fill="none"/>',
        '<text x="357" y="239" font-size="14">Intersection: ρ = 1.4</text>',
        '<text x="357" y="264" font-size="14">Rotate to obtain one circle.</text>',
        '<text x="357" y="289" font-size="14">Replace it by a tunnel belt.</text>',
        '<text x="26" y="355" font-size="14">Bowl: one end. Catenoid: two ends. The union is singular.</text>',
        '<text x="26" y="382" font-size="14" fill="#58727e">Numerical ODE profiles, not parabola substitutes or the glued solution.</text>',
        '</g></svg>']
    (OUT/'dpn-bowl-catenoid-meridian.svg').write_text('\n'.join(parts)+'\n')


def main():
    for m in COUNTS:
        data = make_model(m)
        name = 'bowl-catenoid-gluing'+('' if m==12 else f'-{m}')
        (OUT/(name+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
        print(m, data['audit'])
    data = make_input()
    (OUT/'dpn-bowl-catenoid-input.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    drawings()


if __name__ == '__main__': main()
