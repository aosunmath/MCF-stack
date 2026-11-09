# Lee–Wang quadric flow illustration

Reviewed source: Yng-Ing Lee and Mu-Tao Wang, *Hamiltonian stationary cones and self-similar solutions in higher dimension*, [arXiv:0802.0359v1](https://arxiv.org/html/0802.0359v1), Theorem 1.1, Propositions 2.1–2.2, and Section 3. The relevant construction, quotient, embeddedness conditions, and weak continuation proof were read. This update is confined to the existing shrinker entry and its illustration; the companion expander is available as an optional positive-time view. No paper or source figure is redistributed.

## Geometry and conventions

Use the unit weights (1, 1, −1), so n = 3, k = 2, S = 1. The intrinsic dimension and codimension are both three, in C³ = R⁶. The time-dependent quadric is x₁² + x₂² − x₃² = −2t. Its circle lift is (eⁱˢx₁, eⁱˢx₂, e⁻ⁱˢx₃), with (x, s + π) identified with (−x, s). This is the mapping torus, retaining the qualification already recorded in the catalogue rather than silently using the source's product-topology shorthand. Smooth slices at t ≠ 0 are embedded in R⁶; projected crossings are not evidence against this.

For t < 0, use x = (√(u² − 2t) cos θ, √(u² − 2t) sin θ, u). This describes Lₜ = √(−t)L₋₁ after reparametrizing u. The normalized slice at t = −1 has H = −X⊥/2. At t = 0 the real slice is a double cone, and the full cone is singular at the origin. At t > 0 use x = (r cos θ, r sin θ, ±√(r² + 2t)). These two real sheets belong to one connected expander after the circle gluing. The source proves Brakke continuation without mass loss; this is not a claim of smooth evolution across zero.

The normal velocity and mean curvature are computed in R⁶, not in the three-dimensional display space. The hyperboloid leaves are not surface mean curvature flows in R³. In particular, the source's word “Hamiltonian stationary” does not mean stationary under MCF.

## Drawing choices

- Four default times: −1, −0.25, −0.04, 0. The optional continuation uses −1, 0, 0.25, 1.
- The physical crop is |X| ≤ 3.6 at every time. Both the camera and units per pixel are shared across time panels. This displays the noncompact cone limit instead of shrinking a bounded material patch to a point.
- Forty-eight angular and thirty-six axial intervals sample each exact leaf. Filled quadrilaterals approximate it only for display; no PDE or ODE is solved. Orange marks the waist at u = 0. Cut edges are not boundaries of the complete manifold.
- The circle-action view projects a selected phase leaf and finitely many entire circle orbits. It does not purport to render the full three-manifold as a surface. In coordinate order (Re z₁, Im z₁, Re z₂, Im z₂, Re z₃, Im z₃), P(z) = (Re z₁, (Re z₂ + Im z₁)/√2, (Re z₃ + Im z₂)/√2) has orthonormal rows. The phase slider is spatial, distinct from the time slider. Dotted orbits can include hidden segments.
- The static SVG and interactive canvas share the coordinate and scene functions. The static plate also works without JavaScript and in print. Canvas shading and depth sorting are illustrative rendering choices, not geometric or curvature data.

## Reproduction and verification

Run `node scripts/generate_lee_wang.mjs`. The original Lagrangian generator no longer overwrites this shrinker asset. No external rendering library is required.

`node --test tests/lee-wang-viewer.test.mjs` checks the quadric constraint, fixed physical truncation, waist and expander tip radii, antipodal identification, dilation law, orthogonal projection, and invalid time inputs. An independent finite-difference trace of the normal Hessian in all six ambient coordinates agrees with the normal time derivative; the same check verifies the Lagrangian condition. These tests validate the implementation, not the source's existence theorem. The fallback SVG is checked against its generator.

Publication checks include all Python and JavaScript tests, the complete build and internal link validation, and desktop/mobile checks of playback, singular-time labeling, the expander option, spatial phase, rotation, zoom, reset, printing, and the JavaScript-free fallback.
