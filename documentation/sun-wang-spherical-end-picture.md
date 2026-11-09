# Spherical-doubling translator: picture review

This update concerns only `ex:catalogue-sun-wang-sphere-doubling-translators`.
Its mathematical object is a smooth embedded three-dimensional hypersurface
in Euclidean four-space, with velocity `e₄` and eternal flow `Σ + t e₄`.
The displayed surfaces are its two-dimensional horizontal cross-sections.
They are not three separate ends or an embedding of the full translator in
three-space. Genus `2m − 1` refers to these cross-sections.

## Sources read

- Sun–Wang, *On Mean Curvature Flow Translators with Prescribed Ends*,
  [arXiv:2301.08224v2](https://arxiv.org/pdf/2301.08224v2): Introduction,
  pp. 1–4; Lemma 2.5, p. 9; equations (3.1)–(3.2) and Lemma 3.2, p. 10;
  Theorem 3.7, p. 12; Theorem 4.1, p. 28; Appendix A, pp. 39–40.
  Equation (3.2) was also inspected in the rendered PDF.
- Kapouleas–McGrath, *Generalizing the Linearized Doubling Approach, I*,
  [arXiv:2001.04240v4](https://arxiv.org/pdf/2001.04240v4):
  Definitions 7.10–7.11 and Remark 7.12, p. 40; Theorem 9.40, pp. 65–66;
  equation (10.3) and Theorem 10.5, p. 66, also inspected in the rendered PDF.

Sun–Wang write the actual end as

```text
(X,z) = (√z [x + uₘ(x,z)ν(x)], z),   x ∈ Sₘ, z sufficiently large,
```

where the normal correction tends to zero. Their auxiliary end, equation
(3.1), omits `uₘ`. The compact core comes from a minimizing completion;
neither it nor the normal correction is computed by this picture. There is
no claim that the auxiliary end itself satisfies the translator equation.
The spherical-doubling specialization combines these two papers; it is not
a separately named construction in Sun–Wang.

## What is drawn

Reuse the reviewed connected mesh from
[the spherical-doubling picture](spherical-doubling-picture.md): two nearby
spherical sheets, joined by `2m` radial necks on two aligned, reflected
latitude circles. The linearized latitude guide is numerical; the sheets,
enlarged necks, and separation are a construction schematic, not a computed
Kapouleas–McGrath shrinker. The existing mesh audit checks orientability,
connectedness, closed vertex links, and Euler characteristic `4 − 4m`.

For `r = z/z*`, the physical-slice view displays `√r` times that mesh in
units of `√z*`, where `z*` is an unspecified sufficiently large reference
height. The camera stays fixed as `r` changes from 1 to 9, making linear
growth visible. This is a spatial height control, not the MCF time variable.
The rescaled view displays the same input mesh for every `r`: the auxiliary
slices coincide after dividing by `√z`; the actual slices converge to `Sₘ`
with the omitted normal correction. No convergence rate is illustrated.

Rotation, zoom, a mesh overlay, and a half-space cutaway are available. The
cutaway initially exposes the inner sheet and actual connected neck walls
of the drawing mesh. Cut edges do not belong to the complete surface.
Choices `m = 6, 10, 14` show different model genera, without asserting that
any of these integers meets the theorem's unspecified large-`m` threshold.
The model does not specify the full three-manifold topology or the index
parameters of the translator construction. No metadata properties, entropy
values, canonical tags, section routes, or reader numbers are changed.

The standalone SVG uses the same mesh at height ratios `1:4:9`, with exact
drawing size ratios `1:2:3`. The third slice is cut away. The slices are
arranged in a diagram; their horizontal placement is not a spatial coordinate
in a projection of four-space. The initial interactive mesh includes a hash
of the source mesh. Alternative bridge counts reuse the original assets.

## Regeneration and checks

Run `python3 scripts/generate_sun_wang_end_picture.py` with NumPy and Pillow.
It writes the initial JSON and a self-contained SVG with raster mesh views
and vector text. The older prescribed-end generator preserves this plate.
Existing topology tests cover every source mesh; the new checks ensure that
the end illustration retains that audited mesh and uses the correct height
scaling and dimensional interpretation. Browser review covers height,
rescaling, bridge counts, cutaway, rotation, zoom, reset, and responsive layout.
The PDFs stay in private research storage and are not exported.
