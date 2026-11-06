#!/usr/bin/env python3
"""Original SVG topology/construction diagrams; no soliton geometry is computed.

Run with Python's standard library. Drawn bridge markers are symbolic and do not
specify a small value of the sufficiently large construction parameter m.
"""
from html import escape
from pathlib import Path
import math

OUT = Path(__file__).resolve().parents[1] / "site" / "assets" / "solitons"
BG, INK, ACCENT, PALE = "#f7fafb", "#183f52", "#21667f", "#dcecf1"


def text(x, y, content, size=16, anchor="start", bold=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{"bold" if bold else "normal"}" fill="{INK}">'
            f'{escape(content)}</text>')


def line(x1, y1, x2, y2, width=2, dash=None, arrow=False, color=ACCENT):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    extra += ' marker-end="url(#arrow)"' if arrow else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{width}"{extra}/>')


def ellipse(cx, cy, rx, ry, fill="none", width=2, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
            f'fill="{fill}" stroke="{ACCENT}" stroke-width="{width}"{extra}/>')


def path(d, width=2, fill="none", color=ACCENT):
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{width}"/>'


def dot(cx, cy, r=4):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ACCENT}"/>'


def torus_icon(cx, cy, size):
    """A topological torus icon, expressly not an Angenent torus profile."""
    body = [ellipse(cx, cy, size, .56*size, PALE, 2.5),
            ellipse(cx, cy-.05*size, .54*size, .20*size, BG, 2.5)]
    body += [path(f'M {cx-size*.84} {cy-size*.14} '
                  f'C {cx-size*.58} {cy-size*.61}, {cx+size*.58} {cy-size*.61}, '
                  f'{cx+size*.84} {cy-size*.14}', 1)]
    return body


def doubled_sphere_icon(cx, cy, radius):
    """Symbolic nearby sheets and selected sites on two latitude circles."""
    body = [ellipse(cx, cy, radius, radius, PALE, 2.5),
            ellipse(cx, cy, radius*.85, radius*.85, BG, 2),
            ellipse(cx, cy, radius*.28, radius, width=1, dash="4 5")]
    for sign in [-1, 1]:
        lat_y = cy + sign*radius*.43
        body += [ellipse(cx, lat_y, radius*.78, radius*.18, width=1.5, dash="4 4")]
        # Symbols indicate repeated bridge sites, not a count of the actual necks.
        for theta in [0, math.pi/3, 2*math.pi/3, math.pi, 4*math.pi/3, 5*math.pi/3]:
            body += [dot(cx+radius*.78*math.cos(theta),
                         lat_y+radius*.18*math.sin(theta), max(3, radius*.042))]
    return body


def write(name, title, subtitle, footer, body, description):
    OUT.mkdir(parents=True, exist_ok=True)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{ACCENT}"/></marker></defs>
<rect width="640" height="410" fill="{BG}"/>
<g font-family="Arial, Helvetica, sans-serif" stroke-linecap="round" stroke-linejoin="round">
{text(26,34,title,21,bold=True)}
{text(26,62,subtitle,16)}
{''.join(body)}
{line(26,362,614,362,1,color="#c5d8df")}
{text(26,388,footer,15)}
</g></svg>
'''
    (OUT / (name + ".svg")).write_text(svg, encoding="utf-8")


def toroidal_end():
    body = [text(320,104,"slice(z) = √z [S + uν],    u → 0",18,"middle"),
            text(166,146,"Toroidal cross-section",16,"middle"),
            text(469,146,"Same end, higher slice",16,"middle")]
    body += torus_icon(166,225,85)
    body += torus_icon(469,225,113)
    body += [line(274,225,340,225,arrow=True), text(307,202,"√z growth",15,"middle"),
             text(166,307,"height z₁",17,"middle"),
             text(469,307,"height z₂ > z₁",17,"middle"),
             text(320,343,"One end: T² × [z₀, ∞); correction u is unknown",16,"middle")]
    write("sun-wang-torus-end", "Torus sections along one translator end",
          "Three-dimensional translator in R⁴; horizontal slices lie in R³",
          "Schematic auxiliary cross-sections; no translator is computed.", body,
          "Two schematic toroidal cross-sections at increasing height illustrate square-root growth along a single end of a three-dimensional translator in four-dimensional Euclidean space. The high-height slice is square root of z times a normal graph over an Angenent torus with an unknown correction tending to zero. The ring icons are topological schematics, not computed Angenent tori or exact translator geometry.")


def doubled_sphere_end():
    body = [text(320,104,"slice(z) = √z [S + uν],    u → 0",18,"middle")]
    body += doubled_sphere_icon(165,215,70)
    body += doubled_sphere_icon(469,209,90)
    body += [line(269,215,350,215,arrow=True), text(308,191,"√z growth",15,"middle"),
             text(165,319,"height z₁",17,"middle"),
             text(469,319,"height z₂ > z₁",17,"middle"),
             text(320,346,"One end; cross-sectional genus 2m − 1",16,"middle")]
    write("sun-wang-doubled-sphere-end", "High-genus sections along one translator end",
          "Three-dimensional translator in R⁴; horizontal slices lie in R³",
          "Schematic sections; u is unknown and m must be large.", body,
          "Two topological diagrams of a connected doubled-sphere cross-section at different heights illustrate the single end of a three-dimensional translator in Euclidean four-space. Cross-sectional genus is 2m minus 1 for sufficiently large m. The dots are symbolic repeated bridge sites and do not fix m. Growth is square root of height with an unknown normal correction. Neither the input shrinker nor the resulting translator is computed.")


def spherical_doubling():
    body = [text(183,108,"Two nearby sphere sheets",16,"middle"),
            text(482,108,"Local bridge model",16,"middle")]
    body += doubled_sphere_icon(183,224,101)
    # Two sheet patches joined by the schematic sides of a catenoidal bridge.
    body += [line(374,172,448,172,2.5), line(516,172,590,172,2.5),
             line(374,264,448,264,2.5), line(516,264,590,264,2.5),
             path('M 448 172 C 479 192, 479 244, 448 264', 3),
             path('M 516 172 C 485 192, 485 244, 516 264', 3),
             line(482,150,482,283,1,dash="4 5"),
             text(482,314,"2m bridges; g = 2m − 1",17,"middle"),
             text(183,347,"Bridge sites are symbolic",15,"middle"),
             text(482,347,"m sufficiently large",16,"middle")]
    write("sphere-doubling-shrinker", "Spherical-doubling shrinker in R³",
          "m bridge sites on each of two latitude circles",
          "Construction schematic; the displayed dots do not fix m.", body,
          "A schematic of two nearby sphere sheets with symbolic bridge sites on two latitude circles, beside a local catenoidal bridge model. The Kapouleas–McGrath subfamily has two m bridges and genus two m minus one for sufficiently large m. This is a construction diagram, not an exact or numerically computed self-shrinker; the number of drawn dots does not specify a permitted construction parameter.")


def main():
    toroidal_end()
    doubled_sphere_end()
    spherical_doubling()


if __name__ == "__main__":
    main()
