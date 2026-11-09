# Numerical Δ-wing picture

The picture replaces the strip-and-grim-limit schematic with a numerical
approximation of the surface. The permanent example and section routes are
unchanged. No geometric property metadata is changed by this illustration.

## Source and normalization

Read: the supplied 28-page July 5, 2018 preprint of Hoffman, Ilmanen, Martín,
and White, *Graphical Translators for Mean Curvature Flow*,
[arXiv:1805.10860v2](https://arxiv.org/abs/1805.10860v2): equations (1.2)–(1.4),
Figure 3, Theorem 2.4, Sections 3–4, and Section 5 through Theorem 5.7.
The current public preprint was also consulted; locators here follow the
supplied edition. The source PDF is not exported.

The source uses velocity −e₃. Reflecting its vertical coordinate gives the
site's velocity +e₃ and graph equation

```text
Q(u) = [(1+u_y²)u_xx − 2u_x u_y u_xy + (1+u_x²)u_yy]
       / (1+u_x²+u_y²) = 1.
```

The selected width is the one in Figure 3: b = π/√2, 2b = √2 π. Equation
(1.4) gives cos θ = π/(2b), so θ = π/4. The source's inverted ratio in
Theorem 2.4 must not be used. Here x is the unbounded strip direction and
|y| < b. The two limiting upward graphs are

```text
g±(x,y) = −2 log cos(y/√2) ± x,
```

after recentering at a point tending to the appropriate end. Their transverse
profiles are exact; their use as limits does not give a closed formula for the
Δ-wing. The full flow is graph(u) + t e₃ for all real t.

## Computation

Sections 3–4 construct the centered complete graph from zero-Dirichlet
translator graphs on rectangles [−L,L] × [−b,b] as L tends to infinity.
The generator implements finite versions of that construction. It solves on
a quadrant with even reflection on the axes, using three-point nonuniform
finite differences, an analytic sparse Jacobian, and damped Newton iterations.
The initial solve uses continuation in the right-hand side from 0.1 to 1;
later solves use interpolated earlier solutions. The origin's height is
subtracted only after solving. The boundary data are not taken from a guessed
closed-form Δ-wing.

The final rectangle has L = 24, with 480 intervals in x (spacing 0.1) and 960
intervals in y, clustered near the strip edges by a sine coordinate. A bicubic
interpolant supplies the display mesh, normals, and section curves. Radial root
finding samples the height contours 0 < u ≤ 6. Those contours form the display
rim; they are not a boundary of the complete translator.

The committed [audit](../site/assets/solitons/delta-wing-audit.json) records:

| Diagnostic | Observed value |
| --- | ---: |
| Maximum interpolant PDE residual at 27,915 sample points with u ≤ 6 | 0.000604 |
| Minimum sampled Hessian eigenvalue in that patch | 0.00405 |
| Maximum height change, L = 22 versus 24 at fixed grid spacing | 0.00623 |
| Maximum height change, 720 versus 960 y intervals at L = 24 | 0.00817 |
| Apex second derivatives in x and y | 0.24427, 0.75573 |

These are floating-point diagnostics, not rigorous error estimates. The grid
comparison refines the transverse direction; x spacing stays 0.1. Finite-domain
error, interpolation error, and triangulation error remain. Positive sampled
curvature does not prove convexity between samples. Existence and strict
convexity of the complete surface come from the paper, not this computation.

## Reading the picture

- **Surface:** rotate and zoom; trim the height between 3 and 6. Gold curves
  mark the symmetry sections. Contours mark integer heights.
- **Cutaway:** hide the y > 0 half to expose the rounded center and the
  longitudinal symmetry section. The cut is a viewing aid.
- **Along the strip:** the numerical y = 0 profile has a rounded minimum.
  Dashed reference lines have slopes ±1 and are aligned with the numerical
  profile at x = ±8. Their intercept is not a computed asymptotic constant.
- **Across the strip:** move x from 0 to 6; each curve has u(x,0) subtracted.
  The dashed comparison is the exact limiting tilted grim-reaper profile.

The PNG and SVG are original plots of the computation, not reproductions of
the paper's image. The static drawing remains available without JavaScript
and when printing.

## Reproduction and validation

Using a Python environment with NumPy, SciPy, and Matplotlib:

```sh
python scripts/generate_delta_wing.py --cache /tmp/mcf-delta-cache
```

The cache contains only disposable numerical grids. The ordinary website
build uses the committed assets and needs none of these numerical packages.
Tests check the displayed mesh's disk topology, consistent upward orientation,
normalization at the minimum, profile symmetry, the tilted grim equation,
and profile interpolation. Desktop/mobile reader checks exercise rotation,
zoom, height cuts, profile selection, reset, print, and the static fallback.
