"""Generate original diagrams for four newly reviewed shrinker constructions.

Only Python's standard library is required. The figures represent construction
inputs, topology, symmetry, or qualified asymptotic geometry. None represents a
computed solution. In particular, the variational torus diagram does not use the
Angenent mesh, and the BNS/Ketover end counts retain their large-genus condition.

Sources: KKM arXiv:1106.5454v3, Theorem 1.1; Drugan--Nguyen
arXiv:1708.08808v1, Theorem 1; BNS arXiv:2110.06027v2, Theorems 1.2--1.3
and Lemmas 2.5--2.6; Ketover arXiv:2407.01240v2, Theorem 1.1.
"""

from html import escape
from pathlib import Path
import math


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site/assets/solitons"
BG = "#f7fafb"
INK = "#183f52"
BLUE = "#21667f"
MUTED = "#6a8793"
PALE = "#e5eff3"
SEAM = "#a9572f"
TAU = 2 * math.pi


class Figure:
    def __init__(self, title, description):
        self.parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" '
            'viewBox="0 0 640 410" role="img" aria-labelledby="title description">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="description">{escape(description)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0 0L10 5L0 10Z" fill="{BLUE}"/></marker></defs>',
            f'<rect width="640" height="410" fill="{BG}"/>',
            '<g font-family="Arial, Helvetica, sans-serif" '
            f'fill="{INK}" stroke-linejoin="round" stroke-linecap="round">',
        ]

    def raw(self, value):
        self.parts.append(value)

    def text(self, x, y, value, size=16, color=INK, weight=400, anchor="start"):
        self.raw(f'<text x="{x}" y="{y}" font-size="{size}" '
                 f'font-weight="{weight}" fill="{color}" '
                 f'text-anchor="{anchor}">{escape(value)}</text>')

    def line(self, points, color=BLUE, width=2, opacity=1, fill="none", dash=None):
        coords = " ".join(f"{x:.3f},{y:.3f}" for x, y in points)
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<polyline points="{coords}" fill="{fill}" stroke="{color}" '
                 f'stroke-width="{width}" opacity="{opacity}"{dashed}/>')

    def ellipse(self, x, y, rx, ry, color=BLUE, width=2, fill="none", dash=None):
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" '
                 f'fill="{fill}" stroke="{color}" stroke-width="{width}"{dashed}/>')

    def box(self, x, y, w, h, fill=PALE):
        self.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                 f'rx="10" fill="{fill}"/>')

    def arrow(self, x1, y1, x2, y2):
        self.raw(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" '
                 f'stroke="{BLUE}" stroke-width="2" marker-end="url(#arrow)"/>')

    def save(self, filename):
        (OUT / filename).write_text("\n".join(self.parts + ["</g></svg>"]) + "\n")


def projection(cx, cy, scale, pitch=.5):
    def project(point):
        x, y, z = point
        return cx + scale*x, cy - scale*(z*math.cos(pitch)-y*math.sin(pitch))
    return project


def angles(count=120):
    return [TAU*i/count for i in range(count+1)]


def ring(radius, z, count=120):
    return [(radius*math.cos(a), radius*math.sin(a), z) for a in angles(count)]


def kkm():
    f = Figure(
        "Kapouleas--Kleene--Møller shrinkers: gluing and end schematics",
        "The left panel shows the exact sphere-plane input configuration, not "
        "a desingularized surface. The right panel is a generic nonplanar cone "
        "schematic, not the computed cone of a KKM shrinker. The theorem gives "
        "one end for every sufficiently large prescribed genus.",
    )
    f.text(28, 36, "KKM high-genus shrinkers", 23, weight=600)
    f.text(28, 64, "Existence for every sufficiently large integer genus", 16, MUTED)
    f.text(175, 103, "Sphere–plane input", 18, anchor="middle")
    f.text(474, 103, "End-shape schematic", 18, anchor="middle")
    p = projection(175, 199, 36)
    plane = [(-2.8, -2.8, 0), (2.8, -2.8, 0), (2.8, 2.8, 0),
             (-2.8, 2.8, 0), (-2.8, -2.8, 0)]
    f.line([p(v) for v in plane], color=MUTED, width=1.3, fill=PALE)
    for phi in [math.pi*i/6 for i in range(1, 6)]:
        f.line([p(v) for v in ring(2*math.sin(phi), 2*math.cos(phi))],
               width=.9, opacity=.75)
    for a in [math.pi*i/6 for i in range(6)]:
        f.line([p((2*math.sin(t)*math.cos(a), 2*math.sin(t)*math.sin(a),
                   2*math.cos(t))) for t in angles()], width=.9, opacity=.75)
    f.ellipse(175, 199, 72, 72, width=1.8)
    f.line([p(v) for v in ring(2, 0)], color=SEAM, width=2.8)
    f.text(175, 294, "S²(2) ∪ P; circle to be resolved", 15, anchor="middle")

    # A homogeneous graph supplies a generic cone picture. Its four oscillations
    # are illustrative and are not assigned the symmetry/genus of a solved example.
    q = projection(474, 199, 38, pitch=.55)

    def cone(r, a):
        return r*math.cos(a), r*math.sin(a), .24*r*math.sin(4*a)

    for r in (.7, 1.3, 1.9, 2.55):
        f.line([q(cone(r, a)) for a in angles()], width=1.1,
               opacity=.65 if r < 2.55 else 1)
    for a in angles(16)[:-1]:
        f.line([q((0, 0, 0)), q(cone(2.55, a))], width=.9, opacity=.6)
    f.text(474, 294, "One nonplanar conical end", 15, anchor="middle")
    f.text(28, 337, "Exactly one end for all constructed large-genus surfaces.", 16)
    f.text(28, 364, "Neither panel is a solved shrinker or its computed cone.", 16)
    f.text(28, 393, "SCHEMATIC • gluing input and asymptotic geometry", 15,
           BLUE, weight=600)
    f.save("kkm-shrinker.svg")


def variational_torus():
    f = Figure(
        "Drugan--Nguyen variational shrinking tori: existence schematic",
        "A generic closed curve in the weighted half-plane illustrates the "
        "orbit space. No numerical geodesic is shown. The torus on the right "
        "is a topology diagram for dimension two, not a computed shrinker. "
        "The construction proves entropy below two in every dimension n at "
        "least two, and is not identified with Angenent's shooting profile.",
    )
    f.text(28, 36, "Drugan–Nguyen variational tori", 23, weight=600)
    f.text(28, 64, "Closed-geodesic existence in a weighted half-plane", 16, MUTED)
    f.text(171, 104, "Weighted half-plane r > 0", 17, anchor="middle")
    f.text(470, 104, "Rotational construction", 17, anchor="middle")
    f.box(50, 125, 244, 159, fill="#edf4f6")
    f.arrow(56, 284, 294, 284)
    f.arrow(171, 284, 171, 125)
    f.text(279, 308, "x", 17)
    f.text(181, 137, "r", 17)
    curve = [(171+53*math.cos(a)+5*math.sin(2*a),
              202-49*math.sin(a)+6*math.cos(2*a)) for a in angles()]
    f.line(curve, width=2.6)
    f.text(171, 308, "No computed geodesic", 15, anchor="middle")
    f.arrow(311, 207, 349, 207)
    f.text(330, 184, "revolve", 15, anchor="middle")

    # An annulus-like topological picture. It is deliberately not derived from
    # the numerical Angenent profile or any claimed variational torus solution.
    f.ellipse(470, 207, 91, 59, width=2.3, fill=PALE)
    f.ellipse(470, 207, 37, 23, width=2.3, fill=BG)
    f.raw(f'<path d="M379 207C407 173 433 163 470 163'
          f'C507 163 533 173 561 207" fill="none" stroke="{MUTED}" '
          'stroke-width="1.2" stroke-dasharray="4 5"/>')
    f.text(470, 308, "Topology only (n = 2)", 15, anchor="middle")
    f.box(28, 326, 584, 62)
    f.text(320, 351, "Proved: Gaussian area = entropy < 2", 20,
           weight=600, anchor="middle")
    f.text(320, 376, "All n ≥ 2 • identity with Angenent’s torus not proved", 15,
           anchor="middle")
    f.save("variational-torus.svg")


def bns():
    f = Figure(
        "Buzano--Nguyen--Schulz shrinkers: symmetry and quantified end statements",
        "The diagram shows only the three horizontal half-turn axes for the "
        "dihedral symmetry of the genus-two case, together with the vertical "
        "axis. It does not plot a self-shrinker. The family exists for all positive "
        "genera, is noncompact with at least one conical end, and is proved to "
        "have exactly one end only for sufficiently large genus. The displayed "
        "Gaussian-area bound is rigorous, not a simulation value.",
    )
    f.text(28, 36, "BNS arbitrary-genus shrinkers", 23, weight=600)
    f.text(28, 64, "Equivariant min–max • existence for every genus g ≥ 1", 16, MUTED)
    f.text(174, 108, "Shown: symmetry axes at g = 2", 15, anchor="middle")
    p = projection(174, 202, 37, pitch=.63)
    f.line([p(v) for v in ring(3, 0)], color=MUTED, width=1,
           fill=PALE, dash="4 5")
    for a in [i*math.pi/3 for i in range(3)]:
        f.line([p((-3*math.cos(a), -3*math.sin(a), 0)),
                p((3*math.cos(a), 3*math.sin(a), 0))], width=2.5)
    f.line([p((0, 0, -2.55)), p((0, 0, 2.55))], color=MUTED, width=1.5,
           dash="4 5")
    f.ellipse(174, 202, 4, 4, color=SEAM, fill=SEAM, width=1)
    f.text(189, 130, "vertical axis", 15, MUTED)
    f.text(174, 295, "Axes only • no surface is plotted", 15, anchor="middle")
    f.box(336, 107, 277, 194)
    f.text(474, 137, "All positive genera", 20, weight=600, anchor="middle")
    f.text(474, 166, "Complete and noncompact", 16, anchor="middle")
    f.text(474, 193, "At least one conical end", 16, anchor="middle")
    f.line([(355, 213), (594, 213)], color=MUTED, width=1, opacity=.45)
    f.text(474, 240, "Exactly one end", 18, weight=600, anchor="middle")
    f.text(474, 267, "proved for sufficiently large g", 15, anchor="middle")
    f.box(28, 324, 584, 63)
    f.text(320, 350, "Gaussian area ≤ 1.02 + 4/e < 3", 21,
           weight=600, anchor="middle")
    f.text(320, 376, "Numerical low-genus shapes and values are separate evidence.", 15,
           anchor="middle")
    f.save("bns-shrinkers.svg")


def ketover():
    f = Figure(
        "Ketover self-shrinking doubled planes: large-genus end schematic",
        "Two generic graphical conical annuli indicate the upper and lower "
        "ends proved for sufficiently large genus. A dashed circle indicates "
        "a schematic neck region, not a collection of solved necks. The "
        "theorem gives entropy less than two for every positive genus and "
        "varifold convergence to a plane with multiplicity two. The figure "
        "is not an exact or numerical self-shrinker.",
    )
    f.text(28, 36, "Ketover’s self-shrinking doubled planes", 23, weight=600)
    f.text(28, 64, "Large-genus end schematic • not a solved surface", 16, MUTED)
    p = projection(201, 207, 44, pitch=.42)
    radii = [1.25, 1.7, 2.3, 3.1]
    for sign, color in [(-1, MUTED), (1, BLUE)]:
        for r in radii:
            f.line([p(v) for v in ring(r, sign*(.18+.24*r))],
                   color=color, width=1.3, opacity=.75)
        for a in angles(14)[:-1]:
            f.line([p((r*math.cos(a), r*math.sin(a), sign*(.18+.24*r)))
                    for r in radii], color=color, width=1, opacity=.6)
    f.line([p(v) for v in ring(1.25, 0)], color=SEAM, width=2.8, dash="5 5")
    # Dashed guides mark a region; they are not physical necks with a genus count.
    for a in [0, math.pi]:
        x, y = 1.25*math.cos(a), 1.25*math.sin(a)
        f.line([p((x, y, -.48)), p((x, y, .48))], color=SEAM,
               width=1.3, opacity=.8, dash="4 5")
    for y, color, label in [(136, BLUE, "Upper conical end"),
                            (279, MUTED, "Lower conical end")]:
        f.line([(390, y-5), (408, y-5)], color=color, width=2.5)
        f.text(421, y, label, 16)
    f.line([(272, 207), (397, 207)], color=SEAM, width=1.3, dash="4 5")
    f.text(412, 203, "Neck-circle", 16, SEAM)
    f.text(412, 225, "schematic", 16, SEAM)
    f.text(28, 323, "Exactly two ends is proved only for sufficiently large genus.", 15)
    f.box(28, 338, 584, 54)
    f.text(320, 360, "Entropy < 2 for every positive genus", 20,
           weight=600, anchor="middle")
    f.text(320, 383, "Large-genus limit: a plane with multiplicity two (2P).", 15,
           anchor="middle")
    f.save("ketover-shrinkers.svg")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for generate in (kkm, variational_torus, bns, ketover):
        generate()
    print("Generated four original 640 x 410 shrinker construction schematics.")


if __name__ == "__main__":
    main()
