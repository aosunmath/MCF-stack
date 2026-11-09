# Chen–Sun compact immortal flow: time illustration

Read source: Jingwen Chen and Ao Sun, *Mean curvature flow with multiplicity 2 convergence in manifolds*, [arXiv:2402.04521v2](https://arxiv.org/abs/2402.04521v2), 9 March 2025. Source PDFs remain outside the repository and published edition.

The illustration uses §2.1 and Figure 1 (PDF pp. 3–4) for the orbit-space coordinates and graph PDE, Definition 3.10 and Figure 2 (p. 11) for smooth reflected profiles, Theorem 3.12 (pp. 12–13) for the selected immortal flow, and §3.3 / Theorem 3.17 (pp. 13–15) for convergence. The paper constructs the critical solution by interpolation, without a closed time profile or a calibrated numerical evolution. Its Figure 2 varies initial data; it is not a sequence of times.

For the actual solution the ambient metric is the unit round product on Sⁿ × R, n ≥ 2. The profile is reflected in y = 0 and x = π/2. At finite time it avoids x = 0, π. The two neck orbits approach the poles only at infinite time, and both sheets converge to y = 0 away from the poles. The closed profile times Sⁿ⁻¹ gives S¹ × Sⁿ⁻¹ topology (a genus-one torus for n = 2). Do not claim a monotone neck radius or a decay rate from the sequence of drawings.

## Original schematic model

The original smooth model is parametrized by s ∈ [0, 2π]:

- x(s) = π/2 − (π/2 − a) cos s;
- y(s) = h tanh(1.7 sin s) / tanh(1.7).

The three illustrative (a, h) pairs are (0.52, 0.20), (0.23, 0.095), and (0.065, 0.028). They respect the n = 2 construction's |y| ≤ 1/4 band and keep both necks positive. They are chosen for readability; neither these values nor their interpolation is a computed PDE solution or a claimed asymptotic expansion. Labels t₁ < t₂ < t₃ express qualitative ordering only. Playback stops at a finite-stage model; the infinite-time limit is a separate selection.

The drawing for n = 2 uses the non-isometric radial coordinate map

(p, y) ↦ (1 + 2y)p, p = (sin x cos θ, sin x sin θ, cos x).

Thus positive and negative y appear as an outer blue and an inner ochre sheet, with the same unit reference sphere. The map is injective on the entire illustrated product band, preserving the schematic topology while changing the metric. In particular the image is not a Euclidean MCF, and y does not represent displacement in an isometric R³ model. Both necks are latitude circles at y = 0. A display-only angular cut reveals the inner sheet; it adds no geometric boundary to the actual closed surface. The limit draws the sphere only once with a multiplicity label, not two separated spheres.

The lower profiles share fixed x and y scales across panels. Each profile point represents a latitude S¹ orbit (Sⁿ⁻¹ in the general construction). Gold dots locate neck orbits; the product equator is x = π/2. A fixed radial scale is used in all surface panels.

## Regeneration and verification

Run `node scripts/generate_immortal_product.mjs` (also called by the legacy Python generator). The fallback SVG and interactive viewer share the same model. Test the reflected profile, finite positive necks, product height bound, radial map, finite-stage endpoints, and single-sphere limit with `node --test tests/immortal-product-viewer.test.mjs`. Run the full Python and JavaScript suites, full build with link checks, and desktop/mobile reader checks before publication.
