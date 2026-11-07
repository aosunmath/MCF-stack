# Shao–Zou plane stacking illustration

The entry retains its permanent labels and route. The replacement is an original,
connected construction schematic, not an exact parametrization, numerical
self-shrinker, or certified approximation. The supplied paper is not exported.

## Source review

Guanhua Shao and Jiahua Zou, *Self-shrinkers with any number of ends in ℝ³ by
stacking ℝ²*, [arXiv:2507.18825v1](https://arxiv.org/abs/2507.18825v1), PDF dated
July 28, 2025, 35 pages. The local PDF has SHA-256
`2041e5cd51409ba6ff0331da40238ac4f10da67fffc7fd2fc587059ed29e9850`.
The PDF is the edition used here; the dynamically generated arXiv HTML may show
a later rendering date.

| Source passage | Consequence for the drawing |
| --- | --- |
| Introduction, pp. 2–3; Theorem 8.1, pp. 31–32 | k = 2J + 1 sheets, m bridges per consecutive pair, k ends, genus (k − 1)(m − 1); m must be sufficiently large for fixed k. |
| Definition 2.28 and Remark 2.29, p. 7 | Even k: prism symmetry Dₘₕ. Odd k: antiprism symmetry Dₘd; horizontal reflection alone is not asserted. |
| Equation (3.7), Lemma 3.9, (3.12), pp. 8–9; Lemma 4.11, p. 12 | Radial linearized solutions and limiting balanced neck radius provide a shape guide. |
| Definition 4.3, p. 11; Remark 5.13, p. 18; (5.15), (5.23), p. 19 | Alternate neck sets have angles 2πj/m and (2j + 1)π/m. Actual finite-m radii are parameters near the limiting radius, not necessarily one identical circle. |
| Definitions 6.2–6.5, pp. 22–23; Definition 6.10, p. 24 | The construction uses catenoidal bridges in Gaussian-metric coordinates, glued into punctured graphical sheets. |
| Lemma 6.20, pp. 25–26; Theorem 8.1 | Ends are conical; slope statements are asymptotic expressions in solved parameters, not formulas for the surface. |

## Geometry and limitations

The generator evaluates the two radial solutions of
`u'' + (1/r − r/2)u' + u/2 = 0`:

- `M(r) = hyp1f1(−1/2, 1, r²/4)`, regular at the origin;
- `U(r) = hyperu(−1/2, 1, r²/4)`, asymptotically linear at infinity.

It numerically solves `M'/M + U'/U − r/2 = 0` on `(1,2)`, obtaining
`r* ≈ 1.51860011206547`. This is the limiting RLD guide (3.12), not the
finite-m solution of the horizontal and vertical matching equations. The
normalized branches `M(r)/M(r*)` and `U(r)/U(r*)` are blended in a display collar
of width 0.32 about r*. The unblended branches are linearized solutions;
the blend and the displayed surface are not.

Sheet amplitudes are illustrative multiples of `−cos(π(j+1/2)/k)`, for
`j = 0,…,k−1`. These preserve the ordering and reflection pattern but do not
compute the source's bridge parameters. The middle sheet for odd k is drawn
with zero height away from its necks. This does not assert that the actual
middle end has exactly zero cone slope.

Each sheet is a triangulated disk truncated at radius 3.2, with circular holes
at its incident neck sites. A bridge reuses the hole boundary indices of both
adjacent sheets. Its radial coordinate is `ρ = a cosh u`; its height is
rescaled and blended onto the sheets. There are no cylinders pasted through
intact sheets and no disks sealing the throats. The Gaussian exponential map,
finite-m tilt, matching corrections, and nonlinear perturbation are omitted.
Consequently even the neck charts are illustrative in Euclidean coordinates.

The patch radius is less than half the minimum distance between neighboring
sites in the combined staggered sets. Other sheets stay outside each bridge's
vertical interval. The generator checks connectedness, orientability, edge
incidence, k boundary loops at the display rim, and the genus. Regression tests
also check vertex links and the staggered site symmetries. These are checks of
the drawing mesh only, not evidence for the shrinker equation.

The reader offers k = 2,…,6, m = 6,10,14, rotation, zoom, mesh, cutaway, top and
side views, display separation, and a plan of alternating sites. None of these
small counts is asserted to satisfy the theorem's existence threshold. Changing
the separation is an ambient linear deformation of the drawing, not a family
of self-shrinkers. The default is k = 4, m = 10, with a cutaway exposing the
thirty necks. The static SVG contains full and cutaway views plus the plan.

## Regeneration and verification

Run `python scripts/generate_shao_zou_geometry.py` with NumPy, SciPy and Pillow
installed. This writes the static SVG, fifteen geometry files and an audit JSON
to `site/assets/solitons/`. The usual build requires none of those extra
packages. The older bulk schematic generator delegates this picture to the new
renderer so it cannot restore the bridge-symbol illustration.

Run the Python and JavaScript tests and the complete website build as described
in the README. Inspect desktop and mobile views, all parameter combinations,
cutaway, neck layout, rotation, zoom, separation, failed model loading, reset,
print and no-JavaScript fallback before publication.
