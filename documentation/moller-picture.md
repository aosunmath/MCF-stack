# Møller’s sphere–torus picture

Reviewed source: Niels Martin Møller, *Closed self-shrinking surfaces in R³ via the torus*, [arXiv:1111.7318v2](https://arxiv.org/abs/1111.7318v2), 18 November 2014. Theorem 1 (pp. 1–2) states the large even genus construction and convergence. Figure 1 (p. 3) depicts the singular configuration before handles are inserted. Figure 2 and Proposition 2.1 (p. 5) identify its meridians and intersection locations. Lemma 2.6 (p. 7) gives the rotational shrinker ODE. The paper uses an axial coordinate x₁; this illustration calls it z.

The displayed sphere has radius 2, in the normalization **H** = −X⊥/2. The blue torus is generated from the existing numerical Angenent meridian in `site/assets/solitons/angenent-torus.json`, whose shooting diagnostics are in `geometry-audit.json`. It is not a circular torus. The diagram illustrates the configuration in the paper; it does not certify identification of a numerical solution with the particular torus in its existence proof. Remark 2.2 explicitly leaves torus uniqueness open.

The two computed intersection circles have `(z, r) ≈ (±0.9062891101, 1.7828740979)`. These are roots of the piecewise-linear sampled profile against `z²+r²=4`, not certified coordinates for the exact ODE. They lie within the radius 0.005 neighborhoods of `(±29/32, 41/23)` in Proposition 2.1. Their numerical agreement is a consistency check, not an independent proof of that proposition.

Run `python3 scripts/generate_moller_geometry.py` to reproduce the JSON and SVG using only the Python standard library. The previous `generate_shrinker_schematics.py` entry point delegates to it. Both meshes include the intersection latitude. The SVG shows the shaded limiting configuration and the generating curves; the interactive figure adds rotation, zoom, sheet visibility, complete/cutaway views, and a meridian view. Dashed red circles are intentionally overlaid through the sheets. Removed sectors and mesh edges are display devices.

The limiting-configuration illustration supplies no handle insertion, finite-genus shrinker, entropy integral, or shrinker-PDE solve. Catalogue properties continue to describe the smooth surfaces in the cited theorem. The original PDF and extracted text are kept outside the repository and are not exported.


## Finite-genus handle models

The supplementary viewer offers genus 8, 16, and 24. These are original illustrative level-set smoothings of the two intersecting sheets, not numerical solutions of the shrinker equation or certified approximations to Møller’s surfaces. Theorem 1 does not specify a numerical genus threshold; these particular values are labels for the models, not existence claims for members of its family. No new catalogue example is added.

In cylindrical coordinates let `S(r,z)=sqrt(r²+z²)−2`. Write the sampled non-circular torus meridian in polar coordinates about `(c,0)`, where `c` is the mean of its inner and outer equatorial radii. A periodic cubic spline `rho(phi)` gives `T(r,z)=sqrt((r−c)²+z²)−rho(atan2(z,r−c))`. Let `(r₀,z₀)` be the upper numerical intersection. The model is the zero set

```text
S T − epsilon² cos(m theta) B = 0,
m = g/2, epsilon = 1.25/m,
B = max(1 − ((r−r₀)² + (|z|−z₀)²)/0.7², 0)³.
```

The compactly supported perturbation alternates the pairing of the four local sheets around each intersection circle, producing handles. Away from the two belts the level set coincides with the sphere–torus input. This polynomial saddle smoothing is a visual model, not the Scherk gluing construction or its nonlinear correction in the cited theorem. The support avoids the axis and equatorial plane; the angular coordinate and absolute value cause no singularities on the support boundary. The cutoff is C². The exported mesh is a piecewise-linear approximation to that illustrative level set.

`scripts/generate_moller_genus_models.py` uses NumPy, SciPy, scikit-image, trimesh, and fast-simplification. It extracts meshes on two grids (144 and 192 samples across the horizontal bounding box), checks closedness, connectedness, consistent orientation, and Euler characteristic, then simplifies the fine mesh to 26,000 triangles and repeats the checks after coordinate rounding. The audit in `site/assets/solitons/moller-genus-audit.json` records `chi = 2−2g`: −14, −30, and −46. These checks establish the combinatorial topology of the exported meshes; they do not verify the shrinker PDE, geometric error, or a theorem about the continuum model.

The WebGL viewer provides a genus selector, rotation, zoom, and mesh display. SVGs for all three genera remain accessible without JavaScript. The existing limiting-configuration figure is retained separately.
