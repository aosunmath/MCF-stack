# Ancient Costa perturbations: picture audit

The catalogue page keeps the Costa case, its genus-one/three-end metadata,
permanent tags, and the distinction from the rotational reapernoid.

## Sources read

- Mramor–Payne, *Ancient and Eternal Solutions to Mean Curvature Flow from
  Minimal Surfaces*, [arXiv:1904.08439v2](https://arxiv.org/abs/1904.08439v2),
  Theorem 1.1 and examples, pp. 3–4; Proposition 2.2, pp. 8–9; §3, pp. 10–14.
  The construction starts with small constant normal offsets, evolves them,
  shifts their first-exit times to zero, and extracts an ancient limit.
  Neither an explicit Costa evolution nor the mode used below is provided.
- O. Michael Melko, *Visualizing Minimal Surfaces*, The Mathematica Journal 12
  (2010), [article and PDF](https://www.mathematica-journal.com/2010/12/22/visualizing-minimal-surfaces/),
  equations (16)–(19), pp. 8–10. Equation (17) supplies the stationary Costa
  parametrization. No source image, source code, or PDF is redistributed.

## Geometry and normalization

An original implementation samples equation (17) on the square torus with
periods 1 and i, deleting the three punctures 0, 1/2, i/2. We evaluate the
Weierstrass functions by rapidly convergent theta series (nine terms),
restoring the zeta quasi-periods after reduction to a centered square.
There is no spatial dilation or translation of the parametrization.
The parameter punctures are cut at radii 0.11, 0.033 and 0.033.
The mesh uses a 72 × 72 interior seed grid plus seven graded circular rings
of 96 vertices at each puncture. A fixed, small deterministic perturbation of
interior points and ring angles removes cocircular Delaunay ambiguities.
Periodic Delaunay triangulation gives 6,061 vertices, 11,840 triangles,
three boundary loops and Euler characteristic −3.
Thus the finite mesh is a genus-one surface with three boundary components.
These boundaries are artificial cuts of the three noncompact ends.

With f = wp and g = sqrt(8π) e1 / wp′, the conformal metric is E |dz|²,
where E = (|wp| + 2π e1² / |wp² − e1²|)² / 4.
The Gauss map supplies consistent unit normals. Independent finite
variation checks compare the computed coordinates with these normals and
metric, test periodic closure, and check conformal harmonicity.

## What the times mean

For the convention H = div ν, MCF has normal velocity −H and linearizes
at a minimal surface to u_t = (Δ_M + |A|²)u. We discretize the positive
first Dirichlet mode on this **truncated domain**. The linear finite-element
operator in conformal coordinates has the form

    (−K + diag(m V)) φ = λ diag(m E) φ,  V = E |A|²,

where K is the parameter-triangle stiffness matrix and m the lumped
parameter area. We impose zero values at the three circular boundary loops
and periodic identification across the square. This is a truncated-domain
boundary condition, not a condition on the complete Costa surface. The
eigenvector is positive in the interior and normalized to maximum 1. The saved model is

    X_model^±(p, τ) = X_Costa(p) ± 0.11 exp(τ) φ(p) ν(p),
    τ = λt ∈ [−5, 0].

Its heights solve the discrete linearized equation, up to the recorded
spectral residual. The surface model obtained by applying these heights
is not asserted to solve nonlinear MCF. This is also not a claimed leading
asymptotic expansion of the particular Mramor–Payne flows. Equal signed
heights illustrate the two sides; no identity of the actual two flows is
inferred. The time origin is arbitrary, with no extinction interpretation.

The default visual displacement is magnified three times; the ×1 option
shows the model scale. Space and time are not rescaled between the four
panels. The stationary limit and reference mesh allow comparison.

## Numerical checks and limitations

`site/assets/solitons/minimal-ancient-audit.json` records the equation residual,
positive mode, topology, grid refinement, and changes of truncation radius.
With the stated cuts, the computed eigenvalues for interior seed grids
52, 72 and 96 are about 1.51137, 1.51098 and 1.51072. Increasing all
parameter cut radii by 15% (shorter ends) gives 1.50769; decreasing them
by 15% (longer ends) gives 1.51214.
This is numerical evidence for the truncated computation,
not a certified global spectral value or a nonlinear error bound.
The positive mode decays strongly toward the end cuts.

## Reproduction

With NumPy and SciPy installed:

```sh
python scripts/generate_minimal_ancient_geometry.py
node scripts/generate_minimal_ancient_plate.mjs
```

The second command uses the same frame formula and camera as the viewer,
producing the four-time static SVG for no-JavaScript, failed-load, and print
reading. The old batch generator checks for these files and cannot overwrite
them with the superseded three-line diagram. The existing site build has
no new Python dependencies; only regenerating this numerical asset uses SciPy.
