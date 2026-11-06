# Abresch–Langer index controls

The curve viewer accepts positive coprime integers `m, ell <= 100` with `1/2 < m/ell < 1/sqrt(2)`. Here `m` is the turning number and `ell` the number of curvature periods. The upper bound is a drawing/performance limit, not a restriction of the classification. Noncoprime indices describe repeated covers and receive a message identifying the primitive pair. Invalid input leaves the last valid curve visible. Presets include (2,3), (3,5), (5,8) and (12,17).

The numerical solver runs locally in the browser; no server, remote script, or new dependency is required. The shared viewer retains rotation, zoom and reset. Reset restores the planar view of the selected curve. The canvas label and numerical status update to match the chosen indices. The static SVG, no-JavaScript fallback and print edition remain the labeled (2,3) reference.

## Source and computation

Checked the supplied published copy of Abresch–Langer, *The normalized curve shortening flow and homothetic solutions*, Journal of Differential Geometry **23** (1986), 175–196: Theorem A (p. 176), Proposition 3.2 (p. 181), and the closing condition and numerical construction (p. 183). The paper uses `n` for the second index; this catalogue uses `ell`. The inventory records the exact supplied PDF hash. No paper or extracted text is redistributed.

The existing entry gives the curvature equation in the scale `Hvec=-Xperp/2`. Writing the support function as `h=2 kappa`, with the normal angle `phi` shifted from the tangent angle, gives

```text
h'' + h = 2/h,
(h')² + h² - 4 log(h) = E,
X(phi) = h(phi)(cos phi, sin phi) + h'(phi)(-sin phi, cos phi).
```

For maximum `a>sqrt(2)`, put `q=log(a/h)` and let `Q>0` be the other root of `D(q)=a²(1-exp(-2q))-4q`. Then `h=a exp(-q)`, `h'=-sqrt(D)` on the descending half-cycle and `dphi=h dq/sqrt(D)`. The substitution `q=Q sin²(u)` removes both endpoint square-root singularities. Endpoint limits are evaluated analytically, and the nearer turning point is used to compute `D` without cancellation.

Composite Simpson quadrature on 1024 intervals computes half the period. Bisection in `a` matches the full period to `2 pi m/ell`; a 2048-interval repeat checks quadrature refinement. Reflection completes one oscillation. Repeating it `ell` times and applying the reconstruction formula gives the curve. The last vertex uses the actual accumulated numerical angle, rather than being forced to equal the first vertex. The displayed closing gap is a floating-point diagnostic, not a certified enclosure.

## Verification

`tests/abresch-langer.test.mjs` compares support maxima with independent SciPy DOP853 integrations of the second-order ODE for five pairs. A geometric test computes curvature from consecutive polygon vertices and checks the shrinker equation, without using the quadrature's energy formula. The bounded-domain test covers all 630 admitted pairs, including the thin-loop (50,99) and nearly circular (70,99) cases. Input validation covers missing, noninteger, nonpositive, out-of-range and noncoprime values.

Publication checks on 2026-11-06: 102 Python tests and 27 JavaScript tests passed, as did the complete build and link validation. Desktop (1280 × 900) and mobile (390 × 844) checks covered presets, typed indices, Enter submission, invalid pairs, the (50,99) case, zoom/reset, formula rendering and horizontal overflow. Citation reopening and tag visibility passed. All 88 source tags and all chapter, section, tag and search routes are retained; the collection still contains only the introduction and four special-solution categories, with 42 catalogue figures.
