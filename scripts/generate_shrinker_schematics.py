"""Generate four original, source-conscious shrinker diagrams using stdlib only.

Run generate_soliton_geometry.py first to supply the numerical Abresch--Langer
curve and Angenent profile. This script neither solves a new shrinker nor
asserts that a schematic is an exact immersion. All output is original SVG.
"""

from pathlib import Path
from html import escape
import json
import math


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site/assets/solitons"
BG = "#f7fafb"
INK = "#183f52"
ACCENT = "#21667f"
MUTED = "#6a8793"
PALE = "#e5eff3"
CROSS = "#a9572f"


class SVG:
    def __init__(self, title, description):
        self.parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" '
            'viewBox="0 0 640 410" role="img" aria-labelledby="title description">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="description">{escape(description)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" '
            'refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0 0L10 5L0 10Z" fill="{ACCENT}"/>'
            '</marker></defs>',
            f'<rect width="640" height="410" fill="{BG}"/>',
            '<g font-family="Arial, Helvetica, sans-serif" '
            f'fill="{INK}" stroke-linejoin="round" stroke-linecap="round">',
        ]

    def raw(self, element):
        self.parts.append(element)

    def text(self, x, y, value, size=16, color=INK, weight=400, anchor="start"):
        self.raw(f'<text x="{x}" y="{y}" font-size="{size}" '
                 f'font-weight="{weight}" text-anchor="{anchor}" '
                 f'fill="{color}">{escape(value)}</text>')

    def path(self, points, color=ACCENT, width=2, opacity=1, fill="none", extra=""):
        coords = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        self.raw(f'<polyline points="{coords}" stroke="{color}" '
                 f'stroke-width="{width}" opacity="{opacity}" fill="{fill}" {extra}/>')

    def ellipse(self, x, y, rx, ry, color=ACCENT, width=2, fill="none", extra=""):
        self.raw(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" '
                 f'stroke="{color}" stroke-width="{width}" fill="{fill}" {extra}/>')

    def arrow(self, x1, y1, x2, y2):
        self.raw(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{ACCENT}" '
                 'stroke-width="2.2" fill="none" marker-end="url(#arrow)"/>')

    def save(self, name):
        (OUT / name).write_text("\n".join(self.parts + ["</g></svg>"]) + "\n")


def round_sphere(svg, cx, cy, radius):
    """Orthographic factor picture of a round two-sphere, not a torus."""
    svg.ellipse(cx, cy, radius, radius, fill=PALE)
    svg.ellipse(cx, cy, radius, radius * .28, width=1.3,
                extra='stroke-dasharray="4 4"')
    svg.ellipse(cx, cy, radius * .30, radius, width=1.3)


def drugan():
    svg = SVG("Drugan's immersed shrinking spheres: topology schematic",
              "A smooth sphere domain maps to an immersed image. Two generic local "
              "sheets illustrate self-intersection. No solved meridian or exact "
              "Drugan surface is represented.")
    svg.text(28, 36, "Drugan’s immersed shrinking spheres", 23, weight=600)
    svg.text(28, 64, "Topology schematic • existence by rotational shooting", 16, MUTED)
    svg.text(158, 112, "Smooth domain S²", 18, anchor="middle")
    svg.text(466, 112, "Two local image sheets", 18, anchor="middle")
    round_sphere(svg, 158, 201, 76)
    svg.ellipse(126, 190, 15, 11, width=2.5, fill="#c8e0e9")
    svg.ellipse(187, 211, 15, 11, color=MUTED, width=2.5, fill="#d8e1e6")
    svg.arrow(259, 201, 334, 201)
    svg.text(297, 184, "X", 22, anchor="middle")
    svg.path([(369, 172), (477, 150), (565, 231), (452, 254), (369, 172)],
             fill="#dce9ef", opacity=.95)
    svg.path([(394, 245), (441, 137), (545, 177), (497, 280), (394, 245)],
             color=MUTED, fill="#e6edf0", opacity=.85)
    svg.path([(416, 195), (518, 222)], color=CROSS, width=3.4)
    svg.text(158, 300, "Distinct patches in the domain", 15, anchor="middle")
    svg.text(473, 300, "Their images can meet", 15, anchor="middle")
    svg.text(28, 337, "The domain remains smooth at an image self-intersection.", 16)
    svg.text(28, 364, "No computed Drugan meridian is represented.", 16)
    svg.text(28, 393, "SCHEMATIC • not a solved surface", 15, ACCENT, weight=600)
    svg.save("drugan-schematic.svg")


def curve_products():
    data = json.loads((OUT / "abresch-langer.json").read_text())
    points = data["vertices"]
    svg = SVG("A closed shrinking curve times a shrinking circle in four-space",
              "The first factor is the numerical Abresch--Langer curve with "
              "rotation index 2 and three curvature periods. The second is the "
              "exact circle of radius square root of two. Their product is a "
              "two-dimensional immersed Lagrangian shrinker in four-space. "
              "The diagram shows factors, not a surface in three-space.")
    svg.text(28, 36, "Products of closed shrinking curves", 23, weight=600)
    svg.text(28, 64, "Factor diagram • dimension 2, codimension 2", 16, MUTED)
    # Both factors use the same spatial scale in their displayed coordinate planes.
    factor_scale = 31
    svg.path([(174 + factor_scale*x, 173 - factor_scale*y) for x, y, _ in points],
             width=2.4)
    svg.ellipse(465, 173, math.sqrt(2)*factor_scale, math.sqrt(2)*factor_scale,
                width=2.5)
    svg.text(321, 184, "×", 38, anchor="middle")
    svg.text(174, 274, "γ ⊂ ℝ² • numerical ODE", 16, anchor="middle")
    svg.text(174, 297, "Abresch–Langer (m, l) = (2, 3)", 15, MUTED, anchor="middle")
    svg.text(465, 274, "S¹(√2) ⊂ ℝ² • exact", 16, anchor="middle")
    svg.text(465, 297, "Round shrinking circle", 15, MUTED, anchor="middle")
    svg.raw(f'<rect x="28" y="319" width="584" height="65" rx="10" fill="{PALE}"/>')
    svg.text(320, 345, "γ × S¹(√2) ⊂ ℝ⁴", 23, weight=600, anchor="middle")
    svg.text(320, 372, "Domain S¹ × S¹; a product diagram, not an ℝ³ surface.", 15, anchor="middle")
    svg.save("curve-products.svg")


def spherical_products():
    svg = SVG("Exact products of round sphere factors as higher-codimension shrinkers",
              "For positive integers p and q, the factors of radii square root "
              "of 2p and square root of 2q give a shrinker of dimension p+q in "
              "Euclidean dimension p+q+2. The displayed example is the circle "
              "of radius square root of two and an orthographic picture of the "
              "two-sphere of radius two; their product belongs to five-space.")
    svg.text(28, 36, "Higher-codimension spherical products", 23, weight=600)
    svg.raw('<text x="28" y="65" font-size="18">S'
            '<tspan dy="-5" font-size="15">p</tspan>'
            '<tspan dy="5">(√(2p)) × S</tspan>'
            '<tspan dy="-5" font-size="15">q</tspan>'
            '<tspan dy="5">(√(2q)) ⊂ ℝ</tspan>'
            '<tspan dy="-5" font-size="15">p+q+2</tspan>'
            '<tspan dy="5">,    p, q ≥ 1</tspan></text>')
    scale = 34
    svg.ellipse(174, 173, math.sqrt(2)*scale, math.sqrt(2)*scale, width=2.5)
    round_sphere(svg, 464, 173, 2*scale)
    svg.text(320, 184, "×", 38, anchor="middle")
    svg.text(174, 267, "p = 1: circle factor", 17, anchor="middle")
    svg.text(174, 290, "Exact radius √2", 15, MUTED, anchor="middle")
    svg.text(464, 267, "q = 2: sphere factor", 17, anchor="middle")
    svg.text(464, 290, "Radius 2 • orthographic view", 15, MUTED, anchor="middle")
    svg.raw(f'<rect x="28" y="313" width="584" height="70" rx="10" fill="{PALE}"/>')
    svg.text(320, 340, "Representative: S¹(√2) × S²(2) ⊂ ℝ⁵", 20, weight=600, anchor="middle")
    svg.text(320, 367, "An exact factor diagram; the 3-manifold is not drawn in ℝ³.", 15, anchor="middle")
    svg.save("spherical-products.svg")


def recover_rotational_profile(data):
    """Read one radius/axis pair per angular row without assuming mesh density."""
    vertices = data["vertices"]
    # In revolution() rows have constant z, with first and last angular vertices equal.
    # The first off-diagonal triangle is [0, row_length, row_length+1].
    row_length = data["faces"][0][1]
    if len(vertices) % row_length:
        raise ValueError("Unexpected surface-of-revolution mesh layout")
    return [(v[2], math.hypot(v[0], v[1])) for v in vertices[::row_length]]


def sphere_profile_intersections(profile, radius=2):
    """Intersect the piecewise-linear numerical profile with the exact sphere.

    The roots are exact for each sampled segment, not for the unsampled ODE.
    Their circles are therefore appropriately labelled numerical intersections.
    """
    result = []
    for (z, r), (z1, r1) in zip(profile, profile[1:]):
        dz, dr = z1-z, r1-r
        a = dz*dz + dr*dr
        b = 2*(z*dz + r*dr)
        c = z*z + r*r - radius*radius
        disc = b*b-4*a*c
        if a == 0 or disc < 0:
            continue
        for t in ((-b-math.sqrt(disc))/(2*a), (-b+math.sqrt(disc))/(2*a)):
            if 0 <= t < 1:
                point = (z+t*dz, r+t*dr)
                if not any(math.dist(point, p) < 1e-6 for p in result):
                    result.append(point)
    if len(result) != 2:
        raise ValueError(f"Expected two intersection circles, found {len(result)}")
    return sorted(result)


def moller_gluing():
    data = json.loads((OUT / "angenent-torus.json").read_text())
    profile = recover_rotational_profile(data)
    intersections = sphere_profile_intersections(profile)
    svg = SVG("Moller gluing construction: sphere and numerical shrinking torus",
              "Original wireframe schematic of the limiting configuration. "
              "The round sphere has radius two. The torus uses the existing "
              "numerical Angenent profile. The two highlighted circles come "
              "from the intersections of its sampled meridian with that sphere. "
              "No desingularized genus-g solution is drawn.")
    svg.text(28, 36, "Møller’s large-genus gluing construction", 23, weight=600)
    svg.text(28, 64, "Limiting configuration • two intersection circles", 16, MUTED)
    pitch, scale = .50, 54

    def project(point):
        x, y, z = point
        return 218 + scale*x, 201 - scale*(z*math.cos(pitch)-y*math.sin(pitch))

    angles = [2*math.pi*i/120 for i in range(121)]
    # Exact sphere wireframe, shown through the torus to expose both interfaces.
    for phi in [math.pi*i/10 for i in range(1, 10)]:
        r, z = 2*math.sin(phi), 2*math.cos(phi)
        svg.path([project((r*math.cos(a), r*math.sin(a), z)) for a in angles],
                 color=MUTED, width=.85, opacity=.65)
    for a in [math.pi*i/10 for i in range(10)]:
        svg.path([project((2*math.sin(p)*math.cos(a), 2*math.sin(p)*math.sin(a),
                           2*math.cos(p))) for p in angles],
                 color=MUTED, width=.85, opacity=.65)
    # Torus wireframe sampled from the generated shrinker, not a circular torus.
    for z, r in profile[::12]:
        svg.path([project((r*math.cos(a), r*math.sin(a), z)) for a in angles],
                 width=1, opacity=.55)
    for a in [2*math.pi*i/18 for i in range(18)]:
        svg.path([project((r*math.cos(a), r*math.sin(a), z)) for z, r in profile],
                 width=1.1, opacity=.70)
    for z, r in intersections:
        svg.path([project((r*math.cos(a), r*math.sin(a), z)) for a in angles],
                 color=CROSS, width=2.7)
    for y, color, label in [(139, MUTED, "Round sphere"),
                            (187, ACCENT, "Numerical torus"),
                            (235, CROSS, "Intersection")]:
        svg.path([(434, y-5), (456, y-5)], color=color, width=3)
        svg.text(468, y, label, 15)
    svg.text(468, 257, "circles", 15)
    svg.text(28, 337, "The interfaces are replaced in the gluing construction.", 16)
    svg.text(28, 364, "The smooth genus-g shrinker is not drawn.", 16)
    svg.text(28, 393, "SCHEMATIC • numerical torus and exact round sphere", 15,
             ACCENT, weight=600)
    svg.save("moller-gluing.svg")
    return intersections


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    drugan()
    curve_products()
    spherical_products()
    intersections = moller_gluing()
    print("Generated four original shrinker SVG diagrams (640 x 410).")
    print("Numerical meridian/sphere intersections (axis, radius):", intersections)


if __name__ == "__main__":
    main()
