# Angenent–You three-reaper flow illustration

The source is Sigurd Angenent and Qian You, *Ancient Solutions to Curve Shortening with Finite Total Curvature*, [arXiv:1803.01399v1](https://arxiv.org/abs/1803.01399v1). Read equation (3), §3.1–3.10, and Figures 9–11 (PDF pp. 2, 8–13). The picture follows the **embedded graphical** construction with monotone asymptote heights, not the immersed constructions of §§2 and 4. The source PDF is not exported.

The mathematical setting is a smooth embedded curve in Euclidean R², intrinsic dimension one and codimension one, with normal velocity equal to its curvature vector. There is no additional factor in time. The selected parameters are `a_k = k*pi`, `k = 0,1,2,3`, and `C_1 = C_2 = C_3 = 0`. Thus every strip has width pi, and the three separate translators have horizontal velocities −1, +1, −1. This agrees with equation (3) and the orientation of Figure 9. When implementing the inverse branches used for gluing, their signs are obtained directly from (3); the odd/even orientation in the text of (12) is opposite to that of (3) and Figure 9.

The eternal solution is obtained in the paper by a subsequential ancient limit of finite-start solutions. The present computation evolves **one finite-start approximation**, beginning at `t = -10`. It neither establishes convergence to that limit nor proves uniqueness. We show times −6 through 9, with six fixed snapshots at −6, −3, 0, 3, 6, 9. Zero is an ordinary time, not extinction. No late-time limit theorem is asserted by the pictures.

## Initial curve and numerical equation

For an odd-indexed strip the exact reaper is `x = log(sin(y-a_(k-1))) - t`; for the even strip its sign is reversed. The two shared-asymptote branches are joined inside `-1 <= x <= 1` with a smooth monotone cutoff, as in §3.2. Our cutoff is `eta(x) = A/(A+B)`, where `A = exp(-1/u)`, `B = exp(-1/(1-u))`, `u = (x+1)/2`, extended constantly outside the gluing interval. Reflection in `y = 3*pi/2` completes the upper half of the initial curve. The initial endpoints are on the exact reaper tails at `x = -32`; they remain fixed for the finite-domain computation. They are outside the displayed window `-12 <= x <= 8`.

The continuum normal equation is `(X_t)^perp = X_ss`; for the graph `x=u(y,t)` it is `u_t = u_yy/(1+u_y²)`. We use a parametric discretization to resolve both the turns and the almost horizontal connecting segments. Each step freezes the arc metric, solves a tridiagonal backward-Euler system for both coordinates, then redistributes points by cubic interpolation in cumulative polygonal arc length. There are 2401 nodes and time step 0.002. The exported 151 frames, spaced by 0.1 time units, are resampled to 901 nodes and rounded to six decimals. Slider interpolation is linear between these computed frames. The browser does not extrapolate beyond the computed time interval.

The six snapshots use identical spatial scale and equal horizontal/vertical units. They depict one connected curve, not three independently evolving components. The optional dashed overlay consists of the **exact separate grim reapers** at the selected time; these approximate the constructed flow only in the distant past. An overlay remains available at later times specifically to show the difference between the separate model translators and the interacting curve. Both noncompact outer ends continue to the left; viewport clipping is not a geometric boundary.

## Reproduction and diagnostics

Use Python with NumPy and SciPy:

```sh
python3 scripts/generate_reaper_flow.py --audit
```

This generates the geometry JSON, original six-panel SVG, and `grim-reaper-chains-audit.json`. The shared schematic generator preserves this drawing rather than overwriting it with the former Bézier cartoon.

The audit compares `x(y,t)` on `0.05 <= y <= 3*pi-0.05` at the six displayed times. With 4801 nodes and time step 0.001, the maximum difference from the displayed calculation is about **0.00659**. Starting at −12 changes it by about **0.00317**; moving the endpoints to −40 with 2801 nodes changes it by about **0.000241**. These are empirical differences, not rigorous error bounds. The audit also evolves a single exact reaper for one time unit (error about 0.00254), checks reflection symmetry, and records the signed-area balance against `d/dt integral u dy = -pi`. Values near machine precision in the far tails are allowed in the graph-monotonicity check.

The original construction, eternal existence, embeddedness and asymptotic statements belong to Angenent–You. The later finite-start shapes and all numerical diagnostics belong to this illustration. No new entropy, uniqueness, stability or asymptotic claim is added to the catalogue metadata.
