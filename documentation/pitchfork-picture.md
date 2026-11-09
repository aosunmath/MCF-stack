# Pitchfork picture: source and limits

The replacement picture was checked against Hoffman–Martín–White,
*Scherk-like Translators for Mean Curvature Flow*,
[arXiv:1903.04617v4](https://arxiv.org/abs/1903.04617v4): the normalization
on p. 2, the overview on pp. 6–8, Theorem 10.1, and Section 12 on
pp. 37–39. Figures 6 (p. 8) and 14 (p. 38) were inspected visually.
The PDF is a research input and is not distributed with the website.

The paper translates downward. The catalogue reflects the vertical coordinate
to translate upward with velocity e₃. The new illustration fixes half-width
w = π, so the slab is −π < y < π; it does not rescale the picture to pretend
to depict the wider pitchforks. The full pitchfork is obtained from one graph
over R × (0, w) by a half-turn (x,y,z) → (−x,−y,z) about its vertical boundary
line. The upward boundary values are −∞ on the negative x-axis, +∞ on the
positive x-axis, and +∞ along y = w. Theorem 12.1 gives negative Gaussian
curvature and the planar and tilted-grim-reaper limits. At w = π the latter
profile is −log sin y, after vertical recentering. The displayed formula in
Theorem 12.1(4) has an apparent recentering typo; the proof on p. 38 explicitly
uses u(a,w/2), which is the normalization used here.

## What was drawn

This is an original **qualitative schematic**, not a finite-difference solution,
a certified approximation, or an explicit pitchfork formula. Its smooth
parametrization is

    X(y,z) = (f(y,z), y, z),       −π < y < π, z ∈ R,
    f(y,z) = ½ sin(y) exp(z) + yz − tan(y/2).

This map was chosen for the drawing, not taken from the paper. The parameters,
horizontal-section heights and distances in this schematic must not be used
as quantitative measurements of the pitchfork. In particular the transition
rate and placement of the grim-reaper-shaped portions are illustrative.

The map preserves several source-supported qualitative features:

- It is an embedding of a strip and is simply connected. The line y = 0 is
  exactly the entire z-axis. The map is smooth there and f_y(0,0) = 0.
- f(−y,z) = −f(y,z), so the two halves meet by the required half-turn.
  For y > 0, f_z = ½ sin(y) exp(z) + y > 0, so this half is also a graph
  z = v(x,y). Its three infinite boundary values have the required signs.
- At fixed bounded x, the low horizontal slices approach y = 0, and the
  high slices approach y = −π, 0, π. These are limiting sheets, not a count
  of topological ends. The complete surface has the topology of a plane.
- For x → +∞ on the positive-y half, solving x = f(y,z) gives
  z = log(2x) − log sin y + o(1) on compact y intervals, so the vertically
  recentered profile has the correct grim-reaper shape for w = π.
- The drawing has negative Gaussian curvature. For y > 0, f_zz > 0 and
  f_yy < 0, hence det(D²f) = f_yy f_zz − f_yz² < 0. The same holds for
  y < 0 with signs reversed. At y = 0 the determinant is
  −(½ exp(z) + 1)² < 0.

These checks do **not** imply the translator equation. For this graph the
upward translator residual has numerator

    (1+f_z²) f_yy − 2 f_y f_z f_yz + (1+f_y²) f_zz
        + f_z (1+f_y²+f_z²),

which does not vanish identically. No PDE accuracy or convergence claim is
made. A quantitatively faithful model would require solving the translator
boundary-value problem with an exhaustion and error/convergence checks.

## Mesh and reader

`scripts/generate_pitchfork_geometry.py` samples the map with extra resolution
near y = ±π, shares the axis vertices, and clips to |x| ≤ 6 and
−3.5 ≤ z ≤ 4.5. All visible outer edges are artificial display cuts. The
retained domain stays away from y = ±π by a factor 0.998. The static SVG embeds
an original rendered image; it does not contain an extracted paper figure.

`site/assets/pitchfork-viewer.mjs` uses depth-tested WebGL and analytic normals.
It supports rotation, zoom, a mesh toggle, one-half inspection, and horizontal
sections with a height slider. The section curves are sampled from the same
map, with clipping performed separately for each line segment so disconnected
pieces are never falsely joined. Gray guides mark y = −π, 0, π. The static
drawing remains available for printing, JavaScript-disabled reading, WebGL
failure, and loss of the graphics context. The former plane-only SVG remains
at its existing asset URL.

Regenerate with `python3 scripts/generate_pitchfork_geometry.py` (NumPy and
Pillow). Geometry tests check mesh connectivity, manifold edges, disk topology,
the shared axis, half-turn symmetry, and negative curvature of the drawing.
JavaScript tests check the section clipping and the one-to-three-sheet limits.
These are checks of the illustration, not a proof about the actual translator.
