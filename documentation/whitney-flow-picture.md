# Whitney sphere: numerical time sequence

The reviewed supplied source is Celso Viana, *A note on the evolution of the Whitney sphere along mean curvature flow*, arXiv:1802.02108v2 (13 pages; SHA-256 `992f374dc9b387fdc371dad9291f068fb5c4cb8ceb5e7e48b8391e2b5c756fd3`). Read the full paper, with the initial formula and collapse result on pp. 1–3, equation (1.1), the reconstruction (2.2), and the symmetry and double-point discussion in Section 2. The illustration is original. Neither the PDF nor its extracted text is exported.

The manuscript retains the general n-dimensional result. This visualization computes only n=2, so the immersion is a two-sphere in C² = R⁴, of codimension two. The initial scale is exactly Viana's formula and the speed is trace mean curvature, `(dF/dt)^perp = Hvec`. The initial profile is analytic. Positive-time shapes are numerical solutions of the reduced PDE, not a closed formula, a prescribed flattening, planar curve shortening, or a homothetic shrinking family.

## Numerical equation and boundary treatment

On `0 <= u <= pi/2`, evolve the upper-right quarter of the figure eight, with `p=(a,b)`, by

```
p_t = p_uu / |p_u|² - p^perp / |p|².
```

The normal part of `p_uu / |p_u|²` is the curvature vector. Its remaining tangential part only chooses a parametrization, so this equation has the same normal velocity as Viana's equation (1.1) for n=2. A centered second-order difference approximates both spatial derivatives. Odd extension through `u=0` fixes the origin and makes its curvature and velocity vanish. The endpoint value is imposed as zero; the singular quotient is evaluated only at nonzero interior nodes. At `u=pi/2`, the reflection `(a,b) -> (a,-b)` imposes `a_u=0, b=0`; the outer tip moves freely along the real axis. These symmetries reconstruct the full smooth figure eight.

`python3 scripts/generate_whitney_flow.py` uses NumPy and SciPy (the initial run used NumPy 2.3.4 and SciPy 1.17.1). A sparse BDF method integrates to physical time 0.09 with `rtol=2e-9`, `atol=2e-11`, maximum step 0.0005, and exports 91 frames spaced by 0.001. There is no interpolation between time frames, extrapolation to extinction, or continuation after the singularity.

The generator compares 320, 640 and 1280 quarter intervals at all output times. The maximum common-node discrepancy is approximately 5.08e-5 between 320 and 640 and 1.27e-5 between 640 and 1280; their ratio is about 4.01. A tenfold tightening of integration tolerances changes the 640-interval solution by at most 6.42e-8 at these nodes. These are observed diagnostics, not a posteriori error bounds. The export samples every fourth node of the 640-interval solution; display triangulation and polyline sampling introduce additional geometric discretization. Full machine-readable results are in `site/assets/solitons/whitney-flow-audit.json`.

Independent checks verify the exact initial formula, the initial outer-tip speed `(-4,0)` in the refinement limit, the geometric shape change, preservation of the displayed symmetries, and the single-cover sphere mesh topology (Euler characteristic 2 with two distinct domain poles sharing the origin). Tests that read the exported data use only the standard library; regeneration requires NumPy/SciPy.

## Reading the pictures

A right lobe, `u in [0,pi]`, generates `F(u,v)=(gamma(u) cos v, gamma(u) sin v)` in C²; the antipodal lobe produces the same image and is not used a second time. In the viewer the four real coordinates are ordered `(Re z1, Re z2, Im z1, Im z2)`. The 4D control rotates coordinates 2 and 4, then drops coordinate 4. Ordinary camera rotations act on the resulting R³ projection. Color distinguishes the two domain hemispheres, not separate components.

The default comparison uses times 0, 0.03, 0.06 and 0.09 on a fixed spatial scale. The profile and surface each keep their respective display scale across time. The surface projection can introduce overlaps beyond the actual double point; the planar profile is provided to make the generating geometry unambiguous. Users can inspect a single profile or projected surface, select any computed frame, play, rotate, and zoom. Playback stops at the final computed frame. Static and print drawings retain the four-time comparison.

Viana's theorem supplies collapse to the origin and the multiplicity-two Lagrangian tangent plane. The last computed frame is a regular numerical snapshot, not the singularity. No extinction time or quantitative blow-up convergence is inferred from these finite-resolution pictures. The tangent plane describes parabolic rescaling and is not shown as an unscaled terminal slice.
