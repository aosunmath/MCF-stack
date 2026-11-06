# Nguyen’s shrinking-saddle picture

The figure for `ex:catalogue-nguyen-shrinking-saddles` shows one connected sphere–plane desingularization, a cutaway, and the unwrapped Scherk ingredient. The global surface is an original construction schematic, **not a numerical self-shrinker, the source’s matched initial surface, or an approximation with a proved error bound**. No Gaussian area or entropy is computed from this drawing.

## Source review

Nguyen, *Construction of Complete Embedded Self-Similar Surfaces under Mean Curvature Flow. Part III*, [arXiv:1106.5272v3](https://arxiv.org/abs/1106.5272v3), was read in the supplied 26-page edition (2 July 2014). The PDF and extracted text remain private. Relevant locators are:

- Theorem 1 and preceding paragraph, p. 2: sufficiently large integer m, genus m−1, complete embedded surface, one conical end; finite reflection and half-turn symmetries; two different spatial limits.
- Section 1.1 and Figure 1, pp. 4–5: unbalancing uses rotational self-shrinking caps, not spheres shifted off the origin. The half-turn symmetry simplifies the gluing compared with constructions needing additional wing parameters.
- Section 2, p. 7: the exact minimal ingredient is `sin(y) = sinh(x) sinh(z)`, periodic with period `2π` along y. Its four wings tend to the two intersecting planes.
- Definitions 3 and 6, pp. 8–9: wrapping map and replacement of the top/bottom wings with cutoff graphs over rotational caps. For `τ = √2/m`, one full turn contains m Scherk periods.
- Equation (5), Definition 9 and Corollary 12, pp. 11–12: ODE construction and matching of the rotational caps.
- Definition 13 and Proposition 14, p. 13: attach the top/bottom wings to caps, the inner wing to a disk, and the outer wing to the plane. This is the initial surface, before the nonlinear correction.
- Definition 21 and Lemma 22, pp. 20–21: the final end is a graph with leading term `r φ(θ)` and decaying remainder. The angular function φ is not supplied as an explicit formula.
- Theorem 24 and Sections 6–7, pp. 22–25: solve the linearized problem, control the quadratic error, and apply the Schauder fixed-point theorem. The drawing does not compute this correction or the selected unbalancing parameter.

The source convention is `Hvec = −Xperp`; multiplying positions by √2 gives this catalogue’s convention `Hvec = −Xperp/2` and input sphere radius 2. The shared sphere–plane/Scherk ingredients also occur in the KKM entry. This does not identify the resulting shrinker families or assert their noncongruence.

## Global drawing

For m = 6, 10, 14 the drawing uses the implicit Scherk equation with y = mθ and the illustrative map

```text
r = 2 exp(x/m) sech(z/m),     h = 2 tanh(z/m),
(X,Y,Z) = (r cos θ, r sin θ, h).
```

The asymptotic plane x=0 maps to the sphere of radius 2, while z=0 maps to the horizontal plane. The four wings therefore approach two caps, an inner disk, and an exterior sheet. At the equator its first-order scale agrees with the normalized wrapping map in Definition 3. The sech/tanh completion is a drawing choice, not Nguyen’s cutoff and ODE matching. The same general sphere–plane drawing map is used in the KKM illustration; only generic clipping and topology utilities are imported from its generator.

A bounded implicit form is sampled on a 221×221×132 Cartesian grid, then simplified and clipped at r=3.65. An illustrative cone is added through the ambient vertical shear

```text
h -> h + 0.055 r sin(mθ) q(r),
q=0 for r≤2.35, q=1 for r≥3.20,
q=10t³−15t⁴+6t⁵, t=(r−2.35)/0.85, between these radii.
```

The chosen sine profile is not the source’s unknown φ, nor is its amplitude an asserted parameter of actual shrinkers. The smooth drawing model has the paper’s half-turn and vertical-reflection symmetries; meshing and simplification preserve them only approximately. The half-turn sends `(θ,h)` to `(−θ,−h)`, and the reflection at `α=π/(2m)+jπ/m` sends θ to 2α−θ, preserving sin(mθ).

The mesh audits give one connected component, one truncation boundary, and Euler characteristics −9, −17, −25, hence model genera 5, 9, 13. Tests also check vertex links, edge orientation, and that the only boundary is at the display radius. These are checks of the drawing’s topology, not an effective existence threshold. Colors label construction regions, not curvature. The cutaway removes the wedge `Y>0.35|X|`; its edges are artificial.

## Local Scherk view

The separate detail is a finite triangulation of the exact minimal surface `sin(y)=sinh(x)sinh(z)`, over approximately `|x|,|z|≤2.15`, `|y|≤2π`. Marching cubes and simplification are followed by projection of vertices back onto this equation. The maximum equation residual of rounded vertices is recorded in `nguyen-audit.json`; flat triangle interiors are only an approximation. Display coordinates are `(y,x,z)` so that the periodic axis is horizontal. This is the unwrapped minimal ingredient, not an exact shrinker or the completed joining belt.

The interactive figure supports rotation, keyboard controls, zoom, mesh display, three illustrative period counts, and full/cutaway/Scherk views. The period selector is disabled for the fixed two-period local detail. Reset restores the default m=10 full view. Failed requests retain the previous valid model; the static plate remains available if WebGL is unavailable or lost. The SVG has a full view, cutaway and local detail with vector labels and embedded original raster renderings.

## Regeneration

Run `python3 scripts/generate_nguyen_geometry.py` with NumPy, scikit-image, fast-simplification, and Pillow. Committed JSON and SVG assets keep the normal build independent of these packages. The generic referenced-shrinker generator preserves this separately generated plate, including when its `--output` option is used.
