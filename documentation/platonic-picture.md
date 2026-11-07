# Ketover Platonic doubling picture

The source is Daniel Ketover, *Self-Shrinking Platonic Solids*,
[arXiv:1602.07271v1](https://arxiv.org/pdf/1602.07271v1), 23 February 2016.
The paper was read directly, including the introduction, catenoid estimate,
two-parameter sweepout and degeneration arguments. It has no surface figure or
mesh to reproduce; p. 2 points to Chopp's numerical illustrations. No paper
image, supplied PDF, or extracted full text is redistributed here.

## Source-supported structure

- Theorem 0.1, p. 2: embedded surfaces in Euclidean three-space of genera
  3, 5, 7, 11 and 19, with rotational symmetry groups T12, O24, O24, I60 and I60.
- The explanation immediately below the theorem: two rounded copies of a
  Platonic solid, joined by a neck at each face center. The tetrahedral example
  has four necks and genus three.
- Section 2, pp. 9–10, especially (2.1)–(2.5): the cubical sweepout uses two
  concentric punctured spheres joined along the six coordinate half-axes.
  The drawing follows this spherical model. The neck interpolation is ours;
  it is not the paper's entire two-parameter family or a min-max computation.
- Remark 2.5, pp. 14–15: the other face-center configurations use the same
  construction. Cube and octahedron share a rotation group but have different
  neck locations and counts; likewise dodecahedron and icosahedron.
- Pages 3, 12 and 14 explicitly leave compactness and ends unresolved for the
  limiting shrinkers. A compact sweepout model is not proof of a compact limit.

The normalization is H = <X,nu>/2 with H = div(nu), equivalently
the mean curvature vector is -X-perp/2; the associated flow is
M_t = sqrt(-t) Sigma for t < 0. The schematic has no calibrated shrinker scale,
entropy, residual estimate, or assertion of uniqueness or stability.
The reviewed mathematical properties in `catalogue-properties.json` are
unchanged: the compact meshes do not assign compactness or zero ends to them.

## Reproducible geometry

`scripts/generate_platonic_geometry.py` obtains unit face-center directions
from the distinct outward face normals of each regular polyhedron. For f
faces it removes f disjoint disks from each of two radius-(2 +/- h) spheres
and joins matching boundary loops by radial neck annuli. All seams share
vertices. The connected, closed, orientable mesh has

```text
chi = 2(2-f) = 4-2f,  genus = (2-chi)/2 = f-1.
```

Let d be the minimum angle between face-center directions. The drawing uses
b = min(1.12, 0.84 d), tau = 0.42 b, U = acosh(b/tau), and h = 0.65 tau U.
In a tangent frame (e1,e2) at unit face-center direction n, define

```text
q(t,theta) = cos(t/2) n + sin(t/2) (cos(theta)e1 + sin(theta)e2),
t(u) = tau cosh(u),  -U <= u <= U,
w = clamp((t-0.65b)/(0.35b), 0, 1),  B(w) = w^3(10-15w+6w^2),
z(u) = sign(u) [(1-B(w)) 0.65 tau |u| + B(w) h],
X(u,theta) = (2+z(u)) q(t(u),theta).
```

These are catenoid-inspired charts bent into spherical coordinates, with
radial compression and a smooth transition to the sheets. They are not exact
Euclidean catenoids, minimal necks in the Gaussian metric, or solutions of
the shrinker equation. Outside the patches the sheets are round spheres.
The underlying smooth construction has the face-center symmetry; the finite
triangulation approximates it. The grid uses 5,600 initial sphere samples,
48 vertices per neck ring and 32 intervals along each neck. The patch caps
are disjoint (b < d), and the radial sheets remain positive and ordered
throughout the viewer's separation range 0.6–1.8.

Regenerate with NumPy, SciPy and Pillow available:

```sh
python3 scripts/generate_platonic_geometry.py
```

`platonic-audit.json` records the finite-mesh topology and parameters for all
five choices. Independent tests check connectedness, oriented two-face edge
incidence, circular vertex links, Euler characteristic, the face-center
configurations, and the separate waist loops. These verify the drawing only.

The viewer reuses the spherical doubling renderer and provides solid
selection, rotation, zoom, mesh, cutaway and display separation. Blue, gold
and copper distinguish regions of the same surface. The cutaway removes the
front half without capping it; its edges belong only to the display. The SVG
preserves both the full and cutaway cube views plus five family thumbnails
for printing and use without JavaScript. The batch diagram generator
preserves the new plate.
