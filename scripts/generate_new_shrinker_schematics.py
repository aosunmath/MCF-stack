"""Generate construction diagrams, preserving the separately generated BNS and Ketover surfaces.

Only Python's standard library is required. The figures represent construction
inputs, topology, symmetry, or qualified asymptotic geometry. None represents a
computed solution. In particular, the variational torus diagram does not use the
Angenent mesh, and the BNS/Ketover end counts retain their large-genus condition.

KKM now uses generate_kkm_geometry.py; Ketover uses generate_ketover_geometry.py.

Sources: Drugan--Nguyen
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
    # The reviewed surface picture has its own numerical meshing dependencies.
    # Keep it intact when regenerating the standard-library-only diagrams.
    if not (OUT / "bns-shrinkers.svg").exists():
        raise RuntimeError("Run scripts/generate_bns_geometry.py first")


def ketover():
    # The reviewed topology model has its own meshing dependencies.
    if not (OUT / "ketover-shrinkers.svg").exists():
        raise RuntimeError("Run scripts/generate_ketover_geometry.py first")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for generate in (variational_torus, bns, ketover):
        generate()
    print("Generated construction schematics; retained the BNS and Ketover surface illustrations.")


if __name__ == "__main__":
    main()
