# Drugan numerical picture

The Drugan entry replaces its former topology schematic with an original numerical meridian and a surface of revolution. The interactive reader supports rotation, zoom, a fixed planar meridian view, and an angular cutaway. The cutaway changes visibility, not the solved geometry. Blue denotes the half shot from the upper pole; orange denotes its reflection, traversed in reverse. The complete mesh has two collapsed angular circles at its poles and a spherical parameter domain, although its image self-intersects.

## Source and normalization

Read Gregory Drugan, *An immersed S² self-shrinker*, Transactions of the AMS **367** (2015), 3139–3159, DOI [10.1090/S0002-9947-2014-06051-0](https://doi.org/10.1090/S0002-9947-2014-06051-0), [arXiv:1304.0032](https://arxiv.org/abs/1304.0032). The supplied published PDF has SHA-256 `2bd7af8d848b7baa07fd9a84f259583835e15454a42a3d75eb26dd8eb7ed9160`. Sections 1–6 were read, and the displayed equations, Figure 1 and final reflection argument were visually inspected. No source PDF or extracted paper text is redistributed.

The paper already uses `Hvec = -Xperp/2`; no spatial rescaling is needed. Its radial coordinate `x` is denoted `r` here. The previous entry misidentified the graph equation as (1.3); it is (1.2). Equation (1.3) is the inverse graph equation used at vertical tangents.

For Euclidean arc length `s` and tangent angle `theta` measured from the positive radial direction, the equivalent system is

```text
r' = cos(theta)
z' = sin(theta)
theta' = (r/2 - 1/r) sin(theta) - (z/2) cos(theta).
```

The pole expansion derived from (1.2) is `z=b-b*r²/8-b*(b²+4)*r⁴/1024+O(r⁶)`. Start at `r=1e-4` with this expansion and its derivative, then integrate through `theta=-pi/2` to `theta=-3*pi/2`. Solve for height zero at this second radial turn, using a bracket `b in [0.3,0.5]`. The computed values are `b≈0.3934565610610521` and reflection radius `≈0.8368423874488552`. Reflecting the half curve across `z=0` and reversing its traversal gives the complete numerical meridian, with the topology shown in the paper's Figure 1. Rotation gives the snapshot at `t=-1`; the associated immersed flow is `sqrt(-t) X`, `t<0`.

The generator uses SciPy DOP853 and Brent shooting. It repeats the computation with half the start radius, half the maximum step and tighter tolerances. `site/assets/solitons/drugan-audit.json` records the settings, unrounded reflection residuals and changes between computations. These are floating-point diagnostics, not certified error estimates. The paper proves existence; the numerical root is not a uniqueness result or a certified identification of the supremum in Section 5.

## Reproduction and checks

In a Python environment with NumPy, SciPy and Matplotlib, run:

```sh
python scripts/generate_drugan_geometry.py
```

This writes the interactive JSON, the audit JSON, and the original SVG/PNG figure. Normal website builds use the committed assets and need no numerical packages. Pole coordinates and the reflection height are imposed exactly on the display mesh only after the integration residual has been recorded.

The geometry tests independently difference the exported arc-length samples and compare with the ODE, check reflection symmetry and the nontrivial equatorial crossing, and check that the closed triangulated domain has every edge incident to two faces and Euler characteristic two. The viewer test checks that the cutaway selects angular sectors and that 360 degrees restores every face. These are numerical and infrastructure checks, not mathematical proof certification.

## Publication verification (2026-11-06)

- 102 Python tests and 16 JavaScript tests passed; the complete build and internal link checks passed.
- Desktop (1280 × 900) and mobile (390 × 844) reader checks covered the surface and meridian views, rotation, zoom, the full revolution setting, reset, formula rendering and overflow. No JavaScript errors or MathJax errors were observed.
- Citation disclosure reopened, the reference return link resolved, and Show tags exposed the retained example tag.
- All 66 source tags are unchanged. The five chapter routes, 32 section routes, tag routes and search tags match the preceding special-solution edition; no inherited GMT routes are reintroduced. All 31 catalogue figures remain present, with 18 now interactive.
