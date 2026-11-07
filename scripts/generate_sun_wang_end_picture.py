"""Draw slices of the auxiliary end using the reviewed spherical-doubling mesh.

This does not compute a shrinker or translator. NumPy and Pillow are used only
for the printable plate; the website serves the committed assets.
"""
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
NAME = 'sun-wang-doubled-sphere-end'


def drawing(data):
    width, height = 1200, 810
    vertices = np.array(data['vertices'])
    faces = np.array(data['faces'])
    colors = np.array(data['palette'])
    yaw, pitch = .23, .27
    x, y, z = vertices.T
    a = x*np.cos(yaw)-y*np.sin(yaw)
    b = x*np.sin(yaw)+y*np.cos(yaw)
    q = np.column_stack([a, z*np.cos(pitch)-b*np.sin(pitch), z*np.sin(pitch)+b*np.cos(pitch)])
    surface = Image.new('RGBA', (width*3, height*3))
    painter = ImageDraw.Draw(surface)
    ordered = np.argsort(q[faces, 2].mean(axis=1))
    for cx, ratio, cut in [(150, 1, False), (460, 4, False), (930, 9, True)]:
        xy = np.column_stack([cx+28*np.sqrt(ratio)*q[:, 0], 362-28*np.sqrt(ratio)*q[:, 1]])
        for j in ordered:
            f = faces[j]
            a, b, c = q[f]
            n = np.cross(b-a, c-a); n /= np.linalg.norm(n)
            if n[2] < 0:
                n = -n
            light = .48+.50*max(0, n @ np.array([-.35, .55, .76]))
            rgb = np.rint(colors[data['faceGroups'][j]]*light).astype(int)
            polygon = list(xy[f])
            if cut:
                polygon = []
                for ia, ib in zip(f, np.roll(f, -1)):
                    ya, yb = vertices[ia, 1], vertices[ib, 1]
                    if ya <= 0:
                        polygon.append(xy[ia])
                    if (ya <= 0) != (yb <= 0):
                        polygon.append(xy[ia]+ya/(ya-yb)*(xy[ib]-xy[ia]))
                if len(polygon) < 3:
                    continue
            painter.polygon([(round(3*p[0]), round(3*p[1])) for p in polygon], fill=tuple(int(v) for v in rgb)+(255,))
    stream = io.BytesIO()
    surface.resize((width*2, height*2), Image.Resampling.LANCZOS).save(stream, format='PNG', optimize=True)
    encoded = base64.b64encode(stream.getvalue()).decode('ascii')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">High-genus slices of one translator end in four-space</title>',
        '<desc id="desc">Three separate horizontal slices, shown at a common spatial scale, of a schematic auxiliary end. '
        'Their heights have ratio 1 to 4 to 9, so their sizes have ratio 1 to 2 to 3. '
        'Each is one connected doubled sphere with twenty necks on two aligned latitude circles, of model genus nineteen. '
        'The third slice is cut away to reveal the gold inner sheet and copper necks joining it to the blue outer sheet. '
        'These are two-dimensional slices in three-space of a three-dimensional end in four-space, not three ends or a three-dimensional projection of the entire translator. '
        'The shrinker is schematic and the unknown normal correction and compact core are omitted.</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#456c7c"/></marker></defs>',
        f'<rect width="{width}" height="{height}" fill="#f7fafb"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        '<text x="38" y="49" font-size="30" font-weight="600">One end in ℝ⁴, seen through its horizontal slices</text>',
        '<text x="38" y="83" font-size="20" fill="#58727e">Each slice is a connected surface in ℝ³. The fourth coordinate is the height z.</text>',
        '<text x="600" y="130" text-anchor="middle" font-size="23">X = √z [x + uₘ(x,z)ν(x)],   x ∈ Sₘ,   uₘ → 0</text>',
        f'<image width="{width}" height="{height}" href="data:image/png;base64,{encoded}"/>',
        '<text x="150" y="169" text-anchor="middle" font-size="19">Reference slice</text>',
        '<text x="460" y="169" text-anchor="middle" font-size="19">Same end, higher slice</text>',
        '<text x="930" y="169" text-anchor="middle" font-size="19">Cutaway reveals the connections</text>']
    for cx, ratio, scale in [(150, 1, 1), (460, 4, 2), (930, 9, 3)]:
        parts += [f'<text x="{cx}" y="572" text-anchor="middle" font-size="22" font-weight="600">z = {"z*" if ratio==1 else str(ratio)+"z*"}</text>',
                  f'<text x="{cx}" y="602" text-anchor="middle" font-size="18">linear size {scale}×</text>']
    parts += ['<path d="M90 633H1110" fill="none" stroke="#456c7c" stroke-width="2" marker-end="url(#arrow)"/>',
        '<text x="600" y="661" text-anchor="middle" font-size="18">Increasing height z · separate slices at a common spatial scale, not a 3D embedding</text>',
        '<circle cx="48" cy="695" r="6" fill="#4b8ba3"/><text x="64" y="701" font-size="18">Outer sheet</text>',
        '<circle cx="237" cy="695" r="6" fill="#d3a963"/><text x="253" y="701" font-size="18">Inner sheet</text>',
        '<circle cx="424" cy="695" r="6" fill="#bc744d"/><text x="440" y="701" font-size="18">Connecting necks</text>',
        '<text x="1160" y="701" text-anchor="end" font-size="18">20 bridges · model genus 19</text>',
        '<path d="M38 721H1162" stroke="#cedde3"/>',
        '<text x="38" y="750" font-size="17">SCHEMATIC: enlarged necks; uₘ omitted; no computed shrinker, translator, or compact core.</text>',
        '<text x="38" y="780" font-size="17">z* denotes a large reference height. m = 10 is illustrative; existence requires sufficiently large m.</text>',
        '</g></svg>']
    (OUT/(NAME+'.svg')).write_text('\n'.join(parts)+'\n')


def main():
    source = OUT/'sphere-doubling-shrinker.json'
    data = json.loads(source.read_text())
    data.update(name=NAME, kind='sun-wang-spherical-end',
                ambient_dimension=4, dimension=3, slice_dimension=2,
                description='Horizontal slices of a schematic auxiliary end, with square-root height scaling. '
                'Not a computed shrinker or translator. The normal correction and compact core are omitted.',
                source_mesh=dict(asset=source.name, sha256=hashlib.sha256(source.read_bytes()).hexdigest()),
                end_model=dict(height_ratio=[1, 9], default_ratio=9, reference_height='unspecified sufficiently large z*',
                               correction='omitted, not computed', compact_core='not drawn'))
    (OUT/(NAME+'.json')).write_text(json.dumps(data, separators=(',', ':'))+'\n')
    drawing(data)
    print('Wrote auxiliary-end slice mesh and printable SVG.')


if __name__ == '__main__':
    main()
