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
    # Keep the numerical-profile illustration reproducible from this entry point.
    from generate_torus_translator_geometry import main as generate_torus_end
    generate_torus_end()


def doubled_sphere_end():
    # Preserve the reviewed slice plate; do not replace it with bridge-dot icons.
    if not (OUT / "sun-wang-doubled-sphere-end.svg").exists():
        raise RuntimeError("Run scripts/generate_sun_wang_end_picture.py first")


def spherical_doubling():
    # Preserve the reviewed connected mesh illustration when regenerating icons.
    if not (OUT / "sphere-doubling-shrinker.svg").exists():
        raise RuntimeError("Run scripts/generate_spherical_doubling_geometry.py first")


def main():
    toroidal_end()
    doubled_sphere_end()
    spherical_doubling()


if __name__ == "__main__":
    main()
