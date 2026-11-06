# Buzano–Nguyen–Schulz surface illustration

The original interactive drawing replaces the axes-only diagram. It follows
the qualitative geometry of Figures 3–4 in Buzano, Nguyen and Schulz,
*Noncompact self-shrinkers for mean curvature flow with arbitrary genus*,
[arXiv:2110.06027v2](https://arxiv.org/pdf/2110.06027v2), Section 4,
PDF pp. 13–15. The paper was read with particular attention to the sweepout
in Lemma 2.2 (pp. 4–5), the symmetry discussion (pp. 3–4), the genus argument,
and the limit in Theorem 1.3. No paper image or author mesh is redistributed.

The paper's numerical illustrations use Brakke's Surface Evolver in the ball
of radius eight, with free boundary on the sphere and the Gaussian metric.
Our drawing does **not** reproduce that calculation. It is an independently
chosen implicit model illustrating a connected surface with handles, a central
sheet, rounded upper and lower caps, and a single outer sheet. Its genus can
be selected from 1, 2, 3, 5 and 11. A vertical cut exposes the interior;
gold and blue distinguish the two sides, not separate components.

The theorem proves one asymptotically conical end only for sufficiently large
genus. The low-genus one-ended shapes and the additional vertical reflection
symmetries in the paper are numerical evidence. The illustration includes
these additional features as drawing choices. It asserts neither an exact
parametrization nor a computed approximation to a min-max surface, and does
not identify BNS surfaces with the KKM gluing family. No Gaussian area or
entropy is computed from this mesh.

## Reproducible drawing equation

Set `n = g + 1`, `r² = x² + y²`, and `a_n = 1.35 / n^1.65`. The chosen level set is

```text
z (r² + z² − 4) − a_n Im((x + i y)^n) (1 + r²)^((3 − n)/2) = 0.
```

This is a formula for the **schematic only**, not a formula from the paper or
a solution of the shrinker equation. The coefficients are illustrative.
The factor `Im((x+iy)^n)` is smooth at the axis and makes the drawing invariant
under rotation by `2π/n` and half-turns around the horizontal lines
`theta = jπ/n`. Those lines lie on the level set. At `r=0` the three heights
are `z=−2,0,2`; their tangent planes are horizontal. For large `r`, the outer
sheet has `z/r` tending to the unique real root of
`w(1+w²) = a_n sin(n theta)`. This selects an illustrative cone; it does not
estimate the cone of any BNS shrinker. As the amplitude vanishes, the equation
reduces to the sphere–plane configuration motivating the picture.

`scripts/generate_bns_geometry.py` samples this level set with marching cubes,
simplifies the mesh, clips it at cylindrical radius five, and projects interior
vertices back onto the level set. Projection corrects the drawing equation,
not the shrinker PDE. The generator records connected components, edge
incidences, boundary loops, Euler characteristics and genus in
`site/assets/solitons/bns-audit.json`. Every exported mesh has one component,
one boundary loop, and Euler characteristic `1−2g`. These are checks on the
finite triangulation, not an existence or embedding proof for a self-shrinker.

Regenerate with Python, NumPy, scikit-image and fast-simplification:

```sh
python scripts/generate_bns_geometry.py
```

The WebGL viewer uses the original coordinates and gradient normals, with
depth testing and a clipping plane for the cutaway. Rotation, zoom, mesh,
symmetry-axis and genus controls work with keyboard input. The genus-three
SVG supplies a static fallback and a standalone full/cutaway drawing. The
old batch schematic generator preserves this asset instead of overwriting it.
