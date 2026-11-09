# Ray-avoiding HMW surface illustration

The picture for `ex:catalogue-hmw-platonic-polygon` is an original construction
schematic. It replaces the former rays-only diagram without changing the
entry's permanent tag, route, theorem, or geometric case classifications.

## Source read

Hoffman–Martín–White, *Generating Shrinkers by Mean Curvature Flow*,
[arXiv:2502.20340v3](https://arxiv.org/abs/2502.20340v3), Section 4,
PDF pp. 8–16, including the proofs leading to Theorem 24. Figure 2 on p. 8
was inspected in the PDF; it is Chopp's numerical cubical shrinker, credited
to Chopp in the source. The new drawing uses none of that image or its mesh.

Theorem 12 gives a smooth embedded shrinker avoiding the prescribed rays,
with genus equal to the number of rays minus one, realized by a compact
initial flow. The discussion on pp. 8–9 leaves compactness unresolved in
general and says that sufficiently large polygonal examples are noncompact.
The source's compact numerical picture does not establish compactness of
the surfaces selected by this theorem.

Theorem 24, pp. 15–16, constructs initial surfaces from the radially
projected edge skeleton of a Platonic solid. Its level sets interpolate
between that skeleton and two spheres joined by radial segments through
the face centers. For a regular n-gon the skeleton consists of n pole-to-pole
semicircles halfway between consecutive excluded rays. The construction is
not a parametrization of the final shrinker.

## Original model

`scripts/generate_hmw_rays_geometry.py` creates two radial walls, removes one
spherical disk in each ray direction, and joins matching rims by rounded
passage walls. The compact connected model is the double of a sphere with
q disks removed. Its Euler characteristic is 4 − 2q and its genus is q − 1.
The rays run through the passages into the central cavity. The polygonal
model meets the vertical axis four times, as does the paper's initial
surface (p. 8), rather than suggesting the different Ilmanen–White input.

Most models have base radius 2. For the cubical silhouette the base radial
function is R(u) = 1.64 / (u₁⁴ + u₂⁴ + u₃⁴)^(1/4), for unit u.
These radii are illustration choices, not normalized shrinker dimensions.
Let α be the cap angle, β = 0.46α the throat angle, and d the half gap,
recorded separately for each model in `hmw-rays-audit.json`. A passage at unit
ray v uses directions

    u(t, θ) = cos(a(t)) v + sin(a(t)) (cos θ e₁ + sin θ e₂),
    a(t) = α − (α − β) sin t,
    X(t, θ) = (R(u(t, θ)) + d cos t) u(t, θ),
    0 ≤ t ≤ π, 0 ≤ θ < 2π.

Here e₁,e₂ form an orthonormal basis perpendicular to v. This joins the
outer and inner radial walls with matching tangent planes. The finite mesh
approximates this original model; no shrinker equation or MCF is solved.
All five Platonic ray sets and polygons with n = 3, 5, 7, 12 are included.
These polygon choices do not assert a threshold for noncompactness.

The viewer supports rotation, keyboard controls, zoom, mesh display,
symmetry selection, a depth-tested ray overlay, and a cutaway. Cut edges
are display artifacts. The print/no-JavaScript SVG shows the cube,
its cutaway, and a sevenfold model with the same qualifications.

## Regeneration and checks

Run `python scripts/generate_hmw_rays_geometry.py` in an environment with NumPy,
SciPy and Pillow. The checked-in assets require no numerical library in the
website build. The older schematic generator no longer writes this asset.

The mesh checks verify closed connected orientable manifold topology,
vertex links, genus, normal lengths, and avoidance of every prescribed ray
by every triangle. These checks concern the drawing, not the shrinker PDE.
The usual Python and JavaScript suites, full build with link checks, and
desktop/mobile reader checks are required before publication. No supplied
PDF or private research file is included in the edition.
