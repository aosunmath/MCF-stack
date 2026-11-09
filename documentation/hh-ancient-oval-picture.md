# Haslhofer–Hershkovits ancient oval: time-dependent illustration

The source read for this revision is Haslhofer–Hershkovits, [Ancient solutions of the mean curvature flow, arXiv:1308.4095v1](https://arxiv.org/abs/1308.4095v1), especially Theorem 1.1, Section 3 and Claim 3.5 (PDF pp. 2, 5–7). The figure specializes to the embedded surface case n = 2, j = 1 in Euclidean three-space. It does not represent the higher-dimensional cases. No source PDF or source figure is redistributed.

The paper constructs ancient flows by taking longer capped cylinders, flowing them to extinction, shifting extinction to zero, and rescaling so the major/minor radius ratio is 2 at time −1. Its backward central limit is cylindrical; its selected tip-curvature rescalings converge to a bowl; extinction is round. It supplies no closed formula or computed time slices.

## What is computed

`scripts/generate_hh_ancient_ovals.py` solves rotational mean curvature flow from a finite smooth elongated convex seed: the boundary of the Minkowski sum of the unit ball and an ellipsoid with semiaxes (L, 1/2, 1/2). Its support function is

    h(θ, 0) = 1 + sqrt(L² cos²θ + (1/4) sin²θ),  0 ≤ θ ≤ π/2.

The displayed data use L = 8. L = 6 is a sensitivity comparison. This is a different smooth finite seed from the paper's fixed-cap cylinder family; the numerical agreement is not a proof that its limit is the paper's ancient solution. This distinction appears in the page, caption, data and metadata notes.

Use the outward normal, positive scalar mean curvature for a convex surface, and normal velocity −H. The meridian reconstructed from the support function is

    x = h cosθ − hθ sinθ,
    r = h sinθ + hθ cosθ.

Its principal radii are ρ₁ = h + hθθ and ρ₂ = h + hθ cotθ. Hence h_t = −1/ρ₁ − 1/ρ₂, with hθ = 0 at both symmetry boundaries. At θ = 0 the second radius uses its smooth limit ρ₂ = ρ₁. Reflection and revolution give the closed surface, with one mesh vertex at each pole.

To avoid catastrophic extinction-time subtraction, set b(t) = h(π/2,t), q = h/b, dσ/dt = b⁻² and ℓ = log b. In these units,

    qσ = −Hq + Hq(π/2) q,
    ℓσ = −Hq(π/2).

Here Hq is curvature computed from q. A reflected second-order centered difference grid with 512 intervals and SciPy's BDF method evolves this system, with relative tolerance 2e−9, absolute tolerance 2e−10 and maximum σ step 0.04. The initial seed is first divided by its equatorial radius. The numerical evolution stops when the axial/equatorial ratio reaches 1 + 2e−8.

Write S = (T−t)/b². Backward integration of Sσ = 2 Hq(π/2) S − 1, with spherical terminal value 1/4, avoids cancellation. This terminal value is an approximation; its sensitivity is not a rigorous error bound. The unique decreasing crossing of q(0) = 2 determines the reference time. Remaining time is evaluated through 2ℓ + log S and normalized so that this crossing occurs at t = −1.

The exported 121 time samples run logarithmically from −1000 to −0.001. Each meridian has 129 points, redistributed by arc length after cubic support-function interpolation. The surface revolves the meridian through 40 angular sectors. The time control selects computed samples; it does not morph ellipsoids or claim continuous certified time integration in the browser.

The independent unit-speed bowl comparison integrates f′ = p, p′ = (1+p²)(1−p/r), with the regular tip expansion f = r²/4 + r⁴/128 + O(r⁶), p = r/2 + r³/32 + O(r⁵), starting at r = 1e−5. The tip-view bowl is (−f(r), r), so it points in the correct direction for the right tip's inward translation. It is an ODE approximation, not a paraboloid substitution.

## Reading the views

- **Divide by √(−t):** one fixed spatial scale for the rescaled flow. The snapshot strip and printable four-panel plate also use one common rescaled spatial scale.
- **Original size:** one fixed physical spatial scale, which shows contraction. Very late surfaces become small; zoom remains available.
- **Meridian + limit guides:** gold dashed lines at radius √2 and a dotted circle of radius 2 mark the backward central cylinder and forward extinction sphere in rescaled units. They are limits, not finite-time identities.
- **Right tip + bowl limit:** translate the right tip to the origin, multiply lengths by its mean curvature, and show a local meridian window alongside the bowl. The whole-surface scale selector is disabled in this view. The paper's selected tip-rescaling theorem is distinguished from these arbitrary finite sampled times.

The viewer starts paused, stops before extinction, supports keyboard and pointer rotation, zoom, reduced user motion by default, and a static fallback. Print uses the four-panel plate. No entropy or Gaussian area is inferred from the drawing.

## Numerical checks and reproducibility

`site/assets/solitons/hh-ancient-ovals-audit.json` records the checks. Comparing rescaled support functions on 129 common normal angles at all 121 displayed times gives:

- 256 versus 512 intervals: maximum difference about 0.00228.
- L = 6 versus L = 8 at 512 intervals: maximum difference about 1.55e−7.
- Relative time tolerance 2e−9 versus 4e−10: maximum difference about 3.20e−8.

The normalized round sphere is exactly stationary in the discrete shape equation. The sampled principal radii are positive, the exported profiles have reflection symmetry, their physical dimensions decrease, and the mesh is a closed orientable sphere. These are numerical and implementation checks, not proof evidence or certified error bounds to an ancient solution. Finite-seed agreement on this displayed interval does not validate the remote starting time or arbitrary earlier times.

Regenerate with `python3 scripts/generate_hh_ancient_ovals.py` in an environment with NumPy, SciPy and Pillow. These packages are needed only for regeneration; the website and standard tests use the committed JSON/SVG assets. The old general schematic generator preserves these reviewed assets.
