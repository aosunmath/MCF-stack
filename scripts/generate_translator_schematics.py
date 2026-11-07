#!/usr/bin/env python3
"""Generate original, explicitly schematic diagrams for the translator catalogue.

Only Python's standard library is needed. These are domain, limiting-plane,
local-data, and singular-input diagrams; none claims to compute a translator.
"""
from pathlib import Path
from html import escape
import math

OUT = Path(__file__).resolve().parents[1] / "site" / "assets" / "solitons"
INK, ACCENT, PALE = "#183f52", "#21667f", "#dcecf1"


def text(x, y, value, size=16, anchor="start", weight="normal", color=INK):
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{color}">{escape(value)}</text>')


def line(x1, y1, x2, y2, color=ACCENT, width=2, dash=None, arrow=False, both=False):
    extra = (f' stroke-dasharray="{dash}"' if dash else "")
    extra += ' marker-end="url(#arrow)"' if arrow or both else ""
    extra += ' marker-start="url(#arrow-start)"' if both else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{width}"{extra}/>')


def path(points, color=ACCENT, width=3, dash=None):
    d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{extra}/>'


def ellipse(cx, cy, rx, ry, fill="none", width=2, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" '
            f'stroke="{ACCENT}" stroke-width="{width}"{extra}/>')


def dot(x, y, radius=5):
    return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{ACCENT}"/>'


def write(name, title, subtitle, footer, body, description):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<defs>
 <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{ACCENT}"/></marker>
 <marker id="arrow-start" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 10 0 L 0 5 L 10 10 z" fill="{ACCENT}"/></marker>
</defs>
<rect width="640" height="410" fill="#f7fafb"/>
<g font-family="Arial, Helvetica, sans-serif" stroke-linecap="round" stroke-linejoin="round">
{text(26, 34, title, 21, weight="bold")}
{text(26, 62, subtitle, 16)}
{''.join(body)}
{line(26, 362, 614, 362, color="#c5d8df", width=1)}
{text(26, 388, footer, 15)}
</g>
</svg>
'''
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def delta_wing():
    body = ['<rect x="80" y="112" width="440" height="112" fill="#e7f1f4"/>',
            line(80, 112, 520, 112, dash="7 6"), line(80, 224, 520, 224, dash="7 6"),
            text(300, 154, "Graph domain: ℝ × (−b, b)", 18, "middle"),
            text(300, 188, "(x, y) plane", 16, "middle"),
            line(98, 169, 45, 169, arrow=True), line(501, 169, 542, 169, arrow=True),
            line(562, 116, 562, 220, both=True), text(576, 174, "2b", 18),
            line(89, 271, 198, 313, width=4), line(405, 313, 514, 271, width=4),
            line(88, 317, 206, 317, width=1, dash="4 4"),
            line(397, 317, 520, 317, width=1, dash="4 4"),
            text(146, 342, "x → −∞: tilt −θ", 16, "middle"),
            text(460, 342, "x → +∞: tilt +θ", 16, "middle"),
            text(300, 290, "Limiting tilts", 16, "middle"),
            text(300, 314, "in the (x, z) plane", 15, "middle")]
    write("strip-grim-limits", "Delta-wing: domain and limiting tilts",
          "Width 2b > π; cos θ = π/(2b); upward translation",
          "Domain and tilt directions only; the surface is not plotted.", body,
          "A strip of width 2b greater than pi, with opposite limiting grim-reaper tilt directions. This is a domain and asymptotic-direction diagram, not a delta-wing surface.")


def anisotropy():
    body = [text(158, 109, "Anisotropy (schematic)", 17, "middle"),
            text(461, 109, "Quadratic blow-down", 17, "middle"),
            line(60, 215, 255, 215, width=1, arrow=True),
            line(158, 295, 158, 133, width=1, arrow=True),
            line(366, 215, 558, 215, width=1, arrow=True),
            line(461, 296, 461, 132, width=1, arrow=True)]
    for r in [1, .72, .43]:
        body += [ellipse(158, 215, 85*r, 47*r), ellipse(461, 215, 69*r, 69*r)]
    body += [line(274, 215, 345, 215, arrow=True), text(310, 193, "h → ∞", 16, "middle"),
             text(158, 319, "Nonrotational graph", 16, "middle"),
             text(461, 319, "Active-coordinate slice", 16, "middle"),
             text(320, 348, "Q(x) = |x′|² / [2(k − 1)],     2 ≤ k ≤ n", 17, "middle")]
    write("anisotropic-quadratic", "Higher-dimensional convex translators",
          "Contour diagrams only; no translator surface is plotted",
          "Blow-down may require rotations depending on the scale.", body,
          "Schematic anisotropic contours are rescaled toward circular contours of a quadratic blow-down on its active-coordinate subspace. The theorem allows scale-dependent rotations; this is not an exact translator or a fixed-axis convergence claim.")


def apex():
    # Preserve the reviewed comparison generated by generate_apex_translators.py.
    if not (OUT / "apex-ellipsoid.svg").is_file():
        raise FileNotFoundError("Run scripts/generate_apex_translators.py first")


def end_planes(name, title, periodic):
    body = [line(77, 329, 77, 100, arrow=True), text(36, 213, "z", 19),
            text(111, 119, "z → +∞", 17), text(111, 307, "z → −∞", 17),
            '<rect x="241" y="108" width="335" height="92" rx="8" fill="#e7f1f4"/>',
            '<rect x="241" y="250" width="335" height="92" rx="8" fill="#e7f1f4"/>',
            line(387, 318, 430, 275, width=4),
            text(408, 239, "One plane", 17, "middle")]
    xs = [287, 333, 379, 425, 471] if periodic else [330, 394, 458]
    for x in xs:
        body += [line(x, 177, x+43, 134, width=4)]
    if periodic:
        body += [text(263, 161, "…", 20, "middle"), text(551, 161, "…", 20, "middle")]
    body += [text(408, 96, "Periodic parallel planes" if periodic else "Three parallel planes", 17, "middle")]
    write(name, title, "Height-direction asymptotics for upward translation",
          "Horizontal sections of end planes; this is not the surface.", body,
          ("One asymptotic plane as height tends to minus infinity and an infinite periodic parallel-plane family as height tends to plus infinity. " if periodic else
           "One asymptotic plane as height tends to minus infinity and three parallel planes as height tends to plus infinity. These height-direction limits do not assert four topological ends. ") +
          "Each slanted segment represents a horizontal section of a vertical plane, not a piece of the translator itself.")


def trident():
    body = [text(169, 106, "Cross-section of input", 17, "middle"),
            text(461, 106, "Intersection line", 17, "middle"),
            line(66, 320, 275, 320, width=1, arrow=True),
            line(72, 326, 72, 136, width=1, arrow=True),
            text(279, 326, "x", 16), text(60, 135, "z", 16),
            line(166, 313, 166, 143, width=3, dash="7 5")]
    pts = []
    for i in range(101):
        x = -1.38 + 2.76*i/100
        pts.append((166+65*x, 285+73*math.log(math.cos(x))))
    body += [path(pts, width=4), dot(166, 285, 7),
             text(171, 348, "Grim profile + plane", 16, "middle"),
             line(342, 225, 578, 225, width=3, dash="5 5")]
    for x in [367, 412, 457, 502, 547]:
        body += [ellipse(x, 225, 11, 22, fill=PALE), dot(x, 225, 3)]
    body += [text(461, 178, "Repeated neck locations", 16, "middle"),
             text(461, 284, "Periodic gluing pattern", 16, "middle"),
             text(461, 310, "(schematic)", 16, "middle")]
    write("grim-plane-gluing", "Trident: singular gluing input",
          "Grim-reaper cylinder + vertical plane; upward convention",
          "The crossed input is not the constructed smooth translator.", body,
          "A grim-reaper cross-section and a vertical-plane section intersect. Beside it, repeated marked neck sites along the intersection line illustrate the periodic gluing construction. These are singular input and gluing-location diagrams, not the exact smooth trident surface.")


def finite_genus():
    body = [text(169, 107, "Meridian input (schematic)", 16, "middle"),
            text(467, 107, "Circle of intersection", 17, "middle"),
            line(58, 326, 284, 326, width=1, arrow=True),
            line(63, 333, 63, 130, width=1, arrow=True),
            text(290, 332, "r", 16), text(50, 129, "z", 16)]
    def p(r,z): return (72+57*r, 276-47*z)
    bowl = [p(3.4*i/100, .13*(3.4*i/100)**2) for i in range(101)]
    upper, lower = [], []
    # Parametrizing r = 1+s² keeps both schematic wings smooth at the neck.
    for i in range(101):
        s = math.sqrt(2.4)*i/100
        r = 1+s*s
        upper.append(p(r, .13*r*r+s-.8))
        lower.append(p(r, .13*r*r-s-.8))
    body += [path(bowl, width=4), path(upper, width=3, dash="7 4"), path(lower, width=3, dash="7 4")]
    cross = p(1.64, .13*1.64**2)
    body += [dot(*cross, radius=6), line(cross[0]-7,cross[1]-8,127,185,width=1),
             text(94, 173, "gluing", 15),
             ellipse(467, 229, 73, 73, dash="6 5")]
    for i in range(12):
        a=2*math.pi*i/12
        body.append(dot(467+73*math.cos(a),229+73*math.sin(a),5))
    body += [text(467, 325, "Many small neck sites", 16, "middle"),
             line(83, 348, 116, 348, width=4), text(125, 353, "bowl", 15),
             line(186, 348, 219, 348, width=3, dash="7 4"), text(228, 353, "winglike", 15)]
    write("bowl-catenoid-gluing", "Finite genus: singular gluing input",
          "Bowl + winglike translator; a circle to desingularize",
          "Schematic singular input; the glued surface is not drawn.", body,
          "Schematic meridian profiles of a bowl and a winglike translator meet at a marked point. Rotation produces the intersection circle, shown separately with many neck locations. No displayed profile is an exact or numerically computed translator, and no particular genus is asserted by the number of dots.")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    delta_wing()
    anisotropy()
    apex()
    end_planes("scherkenoid-ends", "Scherkenoid: limiting planes", True)
    end_planes("pitchfork-ends", "Pitchfork: limiting planes", False)
    trident()
    finite_genus()


if __name__ == "__main__":
    main()
