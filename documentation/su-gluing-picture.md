# Su’s glued grim cylinders: slice and translating time views

Reviewed source: Wei-Bo Su, *On the Gluing Construction of Translating
Solitons to Lagrangian Mean Curvature Flow*, [arXiv:2011.07882v2](https://arxiv.org/abs/2011.07882v2).
The Main Theorem and Figure 1 (p. 3), Sections 3.2–3.4 (pp. 8–10), the
potential interpolation in Section 4.1 (pp. 11–12), and the final perturbation
in Theorem 6.10 (p. 28) determine this drawing. Figures 1 and 3 were visually
reviewed. No source figure or PDF is included in the website.

The source has H + T-perp = 0 and F_t = F − tT, with T = −e_m for these
grim cylinders. Our flow time t therefore translates by +t e_m. Su also
uses t for the *gluing scale*; the reading page calls that scale ε. These
are separate parameters. The smooth translator exists for all real flow
times; its shape and gluing scale do not change.

## Geometry and what the picture represents

The displayed representative has m = 3, all three characteristic angles
π/3, and λ = 0. It is a three-dimensional Lagrangian in C³ = R⁶, with
topology S² × R and two ends. It is not a surface in R³.

The exact grim curves intersect at q = −log cos(π/6) + 2πi/3 in the last
complex coordinate. Their real tangent unit vectors have arguments
−2π/3 and −π/3. An equal-angle Lawlor neck in the corresponding tangent
planes is

    (w(s) ω₁, w(s) ω₂, q + exp(−2πi/3) w(s) ω₃),
    w(s) = ε (s+i)^(1/3), s ∈ R, ω ∈ S², 0 < arg w < π/3.

This is the symmetric specialization of the Lawlor geometry in §3.2,
derived without using the polynomial formula printed on p. 8. In
particular Im(w³) = ε³, so w²w′ is real. The spherical tangent directions
are Lagrangian, and the complex volume of three tangent vectors has
constant phase. Thus the full neck is special Lagrangian, after the
displayed unitary rotation. It is minimal, and is not a translator.

For the *drawing only*, we blend this neck into exact grim cylinders
using a quintic cutoff between |w| = 1.5ε and 3ε. Arc-length coordinates
on the grim curves give the correct tangent planes. This coordinate
interpolation is not Su’s interpolation of Lagrangian potentials. Neither
the matching region nor the final translator PDE has been solved. The
displayed ε = 0.22 is illustrative; the theorem does not certify a numerical
threshold for ε.

The surface view restricts to ω₂ = 0, giving a two-dimensional slice of
this model in C² ⊂ C³. It displays
(Re(exp(−iβ)z₁), Im z₃, Re z₃); the angle β changes the forgotten real
coordinate. Rotation subsequently acts on the three displayed coordinates. The optional
half-slice cutaway removes ω₁ > 0, exposing the local neck along its cut edge.
Projection can introduce crossings or degeneracies even though the
constructed translator in C³ is embedded. Outer rims are display cuts.

The profile view selects ω₁ = ω₂ = 0, hence ω₃ = ±1. These two meridians
are not a count of topological ends. The optional dashed input profiles
are exact grim curves. The supplementary SVG shows t = −1, 0, 1 with
identical axes, scale, camera, and ε. Its dot marks the reference point
p + t e₃, not a material point on the smoothed neck. The full domain of
flow time remains R.

## Reproduction and verification

Run `python3 scripts/generate_su_gluing.py`. The general Lagrangian
catalogue generator delegates this entry to it. The interactive viewer
uses the same generated four-coordinate vertices and profiles; time is
added only to Re z₃ before projection. No time-dependent mesh fitting or
camera recentering occurs. Playback is opt-in and stops at the end of the
display interval, when the page is hidden, or when the figure leaves view.

Tests check the input intersection and angles, the symmetric neck’s
Lagrangian and minimal equations by finite differences, the exact far
grim inputs, and translation preserving all four-dimensional pairwise
distances. These tests do not certify the final translator or the
schematic matching. The website’s complete Python and JavaScript suites,
build/link validation, and desktop/mobile reader checks apply as usual.
