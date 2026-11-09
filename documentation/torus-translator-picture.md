# Angenent-torus translator end illustration

The figure for `ex:catalogue-sun-wang-torus-translators` uses Sun–Wang,
*On mean curvature flow translators with prescribed ends*, arXiv:2301.08224v2
(45-page PDF, August 21, 2025 printed date). The reading relevant to the drawing
is Theorem 1.2 (p. 3), the rotationally invariant choice in Section 5
(pp. 34–35), and the parametrization in Appendix A (pp. 39–40).
The HTML rendition currently has a different printed date; the cited PDF is
our version reference. Source: https://arxiv.org/pdf/2301.08224v2.

The actual end has parametrization
`(sqrt(z) [x + u(x,z) nu(x)], z)` with `u` tending to zero. The drawing sets
`u = 0`. It is a leading auxiliary model, not a solved translator, a certified
approximation with error bounds, or a model of a specific minimizing completion.
It provides no compact core, core topology, fattening pair, or numerical cutoff.

The input meridian `(r,q)` is sampled from the existing numerical Angenent torus
asset, in normalization `Hvec = -Xperp/2`. Its reproducible shooting ODE,
return errors, radii, and source mesh SHA-256 are included in the new JSON.
No circular-torus replacement is used. The figure has three views:

- **Rotational quotient:** each point represents a circle in `(x1,x2)`.
  With `h=z/z0`, the plotted coordinates are
  `(sqrt(h) r, sqrt(h) q, h) = (r_actual/sqrt(z0), x3_actual/sqrt(z0), z/z0)`.
  This two-dimensional annulus represents a three-dimensional end in R4.
- **Horizontal torus slice:** restore the rotation angle:
  `sqrt(h) (r cos(theta), r sin(theta), q)` in `R3_x/sqrt(z0)`.
  The camera scale stays fixed while the slider changes height, making the
  square-root growth visible. Height is not flow time.
- **Rescaled end:** divide the horizontal coordinates by `sqrt(z)`.
  The model becomes `(r,q,h)` in the quotient; the actual correction is unknown
  and tends to zero. This coordinate rescaling illustrates cylindrical
  asymptotics; it does not numerically simulate the parabolic blow-down.

The range `1 <= h <= 9` is relative to an unspecified sufficiently large `z0`.
Both rims are display cuts; the bottom is not a tip or a compact core. The
static SVG also displays the selected quotient meridian through the surface
as a guide; the interactive view uses depth testing. Rotation and zoom are
view controls, not construction parameters. The numerical profile is not a
computer-assisted existence proof.

Regenerate with `python3 scripts/generate_torus_translator_geometry.py`.
The existing prescribed-end schematic generator calls it as well.
The JavaScript tests check the annulus and torus Euler characteristics and
boundary edges, the square-root growth, and the normalized constant profile.
