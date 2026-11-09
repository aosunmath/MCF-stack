# Su–Wood stationary Lawlor-profile product: picture audit

The requested entry keeps its route and permanent tags. The new illustration
replaces a single auxiliary curve by the exact two-parameter profile and a
circle reconstruction for the case `m = 3`, `G = SO(2)` in `C³ = R⁶`.
The full object has dimension and codimension three and topology `S¹ × R²`.

## Source and time dependence

Read Su–Wood, *Lagrangian Translating Solitons and Special Lagrangians in Cᵐ
with Symmetries*, [arXiv:2507.01345v1](https://arxiv.org/html/2507.01345v1),
especially Figure 3, Theorems 5.6–5.7, Remark 5.8, equation (31), Proposition
5.9, and Remark 5.10. The corresponding
[published article](https://doi.org/10.1007/s10711-026-01071-4) was also checked.
The example is special Lagrangian, hence minimal: its MCF is **stationary for
every real time**. It does not shrink, expand, translate, or form a neck pinch.
The drawing is original; no paper figures or source PDFs are redistributed.

## Closed formula derived from (31)

For `m = 3`, set `s = arctan(tanh q)`. Direct substitution gives

```text
ell(s) = cosh(q) + i sinh(q),
B(s) = (1/2) asinh(tan(2s)) = q.
```

Fix `mu1 = 1`, `mu2 = mu > 0`, and `phi = 0`. Put
`a = asinh(p)`, `q1 = (a-b)/2`, `q2 = (a+b)/2`. Equation (31) becomes

```text
Z = mu (cosh(b) + i p),
W = (mu² cosh(a+b) - cosh(a-b))/2
    + i ((mu²-1)a + (mu²+1)b)/2,
X(theta,p,b,t) = (Z cos(theta), Z sin(theta), W).
```

The domain is `theta in R/(2pi Z)`, `(p,b) in R²`, `t in R`. No shrinker
or expander normalization is applied. The figure samples `|p| <= 2`,
`|b| <= 1.2` with `0.6 <= mu <= 1.4`; these are display restrictions only.
At `mu = 1` the profile is
`(Re Z, Im Z, Re W, Im W) = (cosh(b), p, p sinh(b), b)`.

## What the viewer displays

- The default profile projection is `(Im Z, Re W, Im W)`. A projection angle
  mixes `Re Z` and `Im Z` before discarding one coordinate. Color records
  `arg Z`; it is not a curvature or flow-time scale.
- The circle view retains all six ambient coordinates before applying
  `(Im z1, Re z3, (Im z3 + Re z2)/sqrt(2))`. It shows one fixed-angle
  two-dimensional leaf with sampled circular group orbits, rather than a
  fictitious surface representing the whole three-manifold.
- The three panels at `t = -2, 0, 2` use identical geometry, scale, crop,
  and camera. Playing time only advances the clock. Profile scale changes
  the stationary solution; orbit angle and projection angle are spatial
  controls. None is passed off as mean curvature flow evolution.
- Cut edges are display truncations. Projection crossings do not contradict
  the embeddedness in `C³` proved for the stated `SO(2)` case. The profile
  itself is not a minimal surface in the projection's Euclidean metric.

## Reproduction and checks

Run `node scripts/generate_su_wood.mjs`. This uses the same formula and
renderer as the interactive figure to generate its JSON and printable SVG.
The older Lagrangian catalogue generator delegates this asset to that script.

`node --test tests/su-wood-viewer.test.mjs` checks the formula against the
original polar coordinates, equality across flow times, the graphical
projection identity, and regeneration of the fallback. Independent finite
differences of the full six-dimensional map check the Lagrangian condition
and constant real holomorphic volume form. These checks catch coordinate or
sign errors; the existence and embeddedness theorem remains the paper's.
