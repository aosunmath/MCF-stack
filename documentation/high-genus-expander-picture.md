# Hoffman–Martín–White expander picture

Source: Hoffman, Martín and White, *Expanders for Mean Curvature Flow and Counterexamples to Ilmanen’s Genus-Reduction Conjecture*, [arXiv:2605.09657v1](https://arxiv.org/abs/2605.09657v1), May 10, 2026. The public PDF was read locally; neither it nor its figure is redistributed.

The illustration uses Theorems 1.1–1.2 (pp. 2–3), the group in Section 2 (p. 7), Definition 3.1 and Figure 1 (pp. 9–10), Definition 4.1 and Theorem 4.3 (pp. 9–11), and Theorem 5.1 (p. 12). Sections 6–7 give the degree argument; Sections 9–10 (pp. 17–31) analyze the circular-boundary model. Theorems 12.6–12.7 (pp. 39–40) preserve genus and the four classes in the limit. The picture does not substitute for proof verification. For incoming genus, retain the statement `2k−2` of Theorem 1.1; the `k−1` in Theorem 13.1 is inconsistent with that statement and is not used here.

## What the picture represents

The source gives complete embedded surfaces in R³, with three conical ends winding around the z-axis and genus `p^a k−1`. The four existence classes are type 1/type 2 crossed with small/big. In a reflection slice, the middle end on the positive-x side connects to the upper end for type 1 and to the lower end for type 2. No slice component is closed. Small/big refers to the integral against the normalized radial cutoff in Definition 4.1, not overall physical size or camera zoom.

The connected mesh represents topology only. It is neither an exact expander nor a numerical PDE approximation, and is not claimed to be an initial surface in the authors’ construction. The old drawing's three upright tubes have been replaced by three broad conical sheets with a connected saddle region. A separate original diagram explains the endpoint pairing. The mesh makes no small/big claim.

## Reproducible drawing model

Run `python scripts/generate_high_genus_expander_geometry.py` with NumPy, scikit-image, fast-simplification and Pillow. Only generic meshing, topology and rasterization helpers are imported from the existing shrinker generators; no mathematical identification with those shrinkers is intended.

Write `r = sqrt(x²+y²)`, `theta = atan2(y,x)` and `S(t) = t³(10−15t+6t²)` clamped to 0 or 1 outside [0,1]. The auxiliary surface is the zero set

```
w³ − A(r) w + B_m(r,theta) = 0,
A(r) = 0.15 [r² − 2.1² (1 − S((r−2.65)/0.45))],
B_m = 0.12 exp(−((r−2.1)/0.45)²) min(r/1.4,1)^m
      [1 − S((r−2.65)/0.45)] cos(m theta).
```

Its displayed height is

```
z = ±0.72 w + 0.035 r cos(4 theta) S((r−2.4)/0.7).
```

The plus sign produces the type 1 pairing; the minus sign produces type 2. Both signs, and all three counts `m = 4,12,20`, have exactly the same exterior cone in the underlying drawing formula for `r ≥ 3.1`:

```
z/r = 0.035 cos(4 theta) + j 0.72 sqrt(0.15),  j = −1,0,1.
```

The three slope functions never meet. The middle one meets z=0 in four lines. This cone has the stated discrete G_4 symmetry, but it is freely chosen, not asserted to be an actual C_k arising from a shrinker, nor to satisfy the unspecified smallness constant in the theorem. The small illustrative k=4 is not an existence bound. The multiplier choices q=1,3,5 illustrate the genus relation m=qk; they do not parametrize actual solutions. No geometric flow or PDE is simulated.

The generated triangulations are truncated at r=3.5. For every mesh, the generator checks connectedness, manifold edge incidence, exactly three boundary loops, and Euler characteristic `1−2m`, giving genus m−1. The public audit repeats these numbers. Coordinate rounding and mesh simplification introduce geometric approximation of the drawing formula only. The camera cutaway removes triangles from display and does not change the stored topology. The cone view omits a tiny neighborhood of the singular vertex for rendering.

## Verification

Python tests independently count mesh edges, components and boundary loops, check orientation, and compare every boundary vertex to the fixed cone formula. JavaScript tests check model routing, the type reflection and winding. Browser checks cover rotation, zoom, all counts, both types, cone and cutaway views, failed model loading, reset, print, no-WebGL fallback, math and mobile overflow. Run the complete project Python and JavaScript suites and the full build with link checks before publishing.
