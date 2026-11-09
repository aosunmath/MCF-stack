# Ketover's Platonic doubling picture

The illustration was rebuilt after reading Daniel Ketover,
[*Self-Shrinking Platonic Solids*, arXiv:1602.07271v1](https://arxiv.org/pdf/1602.07271v1),
23 February 2016, including the full construction and degeneration argument.
Theorem 0.1 and the explanation on p. 2 give genera 3, 5, 7, 11, 19 and
the face-center neck arrangement. Section 2, pp. 9–10, constructs the cubical
sweepout from two concentric spheres with six holes, joined radially.
Remark 2.5, pp. 14–15, covers the other solids. Pages 3, 12 and 14 explicitly
leave compactness and additional ends of the min-max limits unresolved.
The paper contains no surface mesh or explicit formula for those limits.
Its reference to Chopp's figures is not numerical data for this illustration.
No source PDF, source image or extracted paper text is redistributed.

## What the picture represents

The viewer displays **original compact comparison models of the doubling
sweepout**, not a numerical solution of the self-shrinker equation.
Two punctured spheres are joined by one rounded neck in each face-center
direction of a regular solid. If there are f faces, each punctured sphere has
Euler characteristic 2−f. Joining their boundary circles by annuli gives
χ=4−2f and genus f−1. This accounts for all five displayed topologies.
The compactness of these comparison models says nothing about compactness
of the min-max limit; the property catalogue is unchanged.

The mathematical surfaces lie in Euclidean three-space with normalization
H = ⟨X,ν⟩/2 and flow √(−t)Σ for t<0. The illustration uses arbitrary drawing
lengths and is not a time slice of a computed flow. No curvature, entropy,
Gaussian area or residual is inferred from it.

## Reproducible geometry

`scripts/generate_platonic_geometry.py` needs NumPy and Pillow. It builds a
spherical tessellation from the actual polygonal faces of each regular solid.
The vertices are normalized to the unit sphere; face-center directions are
the normalized face averages. Adjacent patches share their outer-edge
vertices exactly. Each patch is an annulus between a circular opening and
the spherical polygon. The two sheet radii are R±h with R=2 and h=0.28.

For a face-center unit vector n and a unit tangent direction u, let β be the
angle from n to the polygon boundary in that direction. Let ρ be the
spherical inradius of the face and α=0.72ρ. Sheet points are

```text
(R ± h) [cos θ n + sin θ u],  α ≤ θ ≤ β.
```

The rounded neck is the annulus

```text
r(t) = R + h cos t,
θ(t) = α (1 − 0.40 sin t),
X(t,u) = r(t) [cos θ(t) n + sin θ(t) u],  0 ≤ t ≤ π.
```

It meets both spherical sheets tangentially; its waist is at r=R. This is
an independently chosen rounded bridge, not an exact catenoid and not a
formula from the paper. The annuli remain inside disjoint spherical face
interiors. Each neck has a strictly monotone radius for 0<t<π. These facts
keep the smooth piecewise model embedded; the mesh checks are separate
finite combinatorial checks. The model is C¹ at the sheet joins, and no
higher regularity or shrinker PDE accuracy is claimed.

The generator uses 12 samples per polygon edge, 10 sheet rings and 20 neck
rings. It checks connectivity, orientability, edge incidences and Euler
characteristic. Independent tests check vertex links, closedness, genus,
the separate waist circles, face-center configurations and finite normals.
These tests audit the illustration only, not the existence theorem.

## Reader controls and fallback

All five solids can be selected. Rotation, zoom, a mesh overlay and a half
cutaway expose the joins and the inner sheet. A display-separation slider
applies r ↦ R+a(r−R), with 0.6≤a≤1.8; this is an orientation-preserving
radial drawing deformation on this shell, not a shrinker parameter.
Reset restores the cubical model, original gap and camera. Blue marks the
outer sheet, gold the inner sheet and copper the connecting necks; they
belong to one connected surface. Cut edges are viewing aids.

The accessible SVG contains original rendered views of the cubical model
and its cutaway, plus all five models with neck and genus counts. It remains
available without JavaScript, without WebGL and in print. The older batch
generator preserves the reviewed asset; regenerate it with the dedicated
script. The existing permanent section and statement tags are retained.
