# Lee–Tsai quotient flow and circle fibers

Source reviewed: Ping-Hung Lee and Chung-Jun Tsai, *Infinite-Time Singularities with Vanishing Mean Curvature for Lagrangian Mean Curvature Flow in Gibbons–Hawking Spaces*, [arXiv:2606.28767v1](https://arxiv.org/html/2606.28767v1). Equations (2.1)–(2.5) specify the geometry, equation (3.2) is the graphical evolution, Sections 4–5 construct and analyze barriers, and Theorem 6.2 and Remark 6.3 give the long-time conclusion and neck scale. No source illustration, PDF, or private research file is redistributed.

## What the picture computes

Four centers lie at −1, −1/3, 1/3 and 1, with regular potential zero (the ALE case). The initial graph is `u(x,0)=0.06(1-x²)`. We solve

`u_t = u_xx / (phi(x,u,0)*(1+u_x²))`, with `u(-1,t)=u(1,t)=0`, for `0 <= t <= 12`.

This is an original numerical illustration, not a closed formula, a barrier-family interpolation, or ordinary curve shortening. Theorem 6.2 provides an existential smallness threshold; we do not certify this specific initial coefficient against it. The infinite-time chain is shown as a separately selected theoretical limit, not a numerical frame reached at t=12.

`generate_lee_tsai_flow.py` uses three-point differences on nonuniform grids with 601, 1201 and 2401 points, graded toward all centers. SciPy's implicit BDF method integrates the resulting tridiagonal system. The 2401-point solution is sampled for the browser at 121 times and 301 spatial points. Playback linearly interpolates these saved frames. Display resampling and interpolation are not additional PDE solves.

The medium/fine maximum height difference is about 6.47e-7, at most 0.0117% of the corresponding frame's maximum height. Tightening the time tolerances tenfold changes height by less than 1.7e-10. The audit also checks positivity, decreasing height, discrete concavity, and reflection symmetry. These are consistency diagnostics, not certified continuum error estimates. Reproduce with NumPy and SciPy installed:

```sh
python scripts/generate_lee_tsai_flow.py
```

The standard build uses the committed assets and requires no scientific Python packages. The old batch schematic generator deliberately skips this figure.

## How to interpret the surface

From `g = phi^(-1) eta² + phi (dx²+dy²+dz²)`, the circle orbit has radius factor `r = phi^(-1/2)` when the circle parameter has period 2π. The surface displayed at `(x,r cos(theta),r sin(theta))` encodes this radius and the quotient ordering. Its horizontal coordinate is the quotient coordinate x, not intrinsic arclength. It is not an isometric embedding or a literal projection of the four-manifold, and it does not evolve by Euclidean MCF. The pale rings are sampled fibers; gold rings mark the two interior-center fibers. Dashed rings are guides, including portions behind the rendered surface.

At finite time, only the outer two fibers collapse, so the lifted surface is a single sphere. In the separate infinite-time limit all four center fibers collapse; three interval lifts form a chain. The actual adjacent spheres intersect transversely in four dimensions. The contact angles and apparent contacts in the 3D diagram do not represent these tangent planes. Colors mark quotient intervals, not separate connected components at finite time.

Every comparison panel uses the same scales. Quotient height is enlarged by a fixed factor of six. The radius diagram uses unaltered phi-derived radii. Rotation and zoom are display operations. The static SVG, no-JavaScript fallback and print view preserve the finite/infinite-time distinction.
